import threading
import datetime
import time
from django.core import management
from django.utils import timezone
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from InfrastructureApp.db.models.ModelObjectUtils import setDefaultCreatedByModifiedByUsers
from ATMDteApp import models
from ATMDteApp.ReportGenerationHelpers import (
    DailyAircraftMovementsBangaloreHelper,
    DailyAircraftMovementsChennaiHelper,
    DailyAircraftMovementsDelhiHelper,
    DailyAircraftMovementsKolkataHelper,
    DailyAircraftMovementsMumbaiHelper,
)
class Command(management.base.BaseCommand):
    help = "This job checks if new entries have been created in DailyAircraftMovements models for the 5 major. If yes, it sends an email to the respective email id."

    def add_arguments(self, parser):
        # Although I've added loc, it's not supposed to do much because Django Docs didn't have call to super()... they had some custom implementation.
        # See https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/
        super().add_arguments(parser)   

    def handle(self, *args, **options):

        # CONSTANTS
        yesterddayDate = timezone.now().date() - datetime.timedelta(days=1)
        MODEL_CLASS_KEY_STRING = 'modelClass'
        REPORT_HELPER_FUNCTION_KEY_STRING = 'reportHelper'
        BUFFER_OBJECT_KEY_STRING = 'bufferObject'
        FILE_NAME_KEY_STRING = 'fileName'
        UPPER_TIME_LIMIT = datetime.time(hour=8, minute=30, second=0)   # we won't send reminders beyond this upper time limit of 8:30 AM Greenwhich time (2:00 PM IST).
        # UPPER_TIME_LIMIT = datetime.time(hour=18, minute=30, second=0)   # This is for testing purposes. Comment the above line before using this.
        smtpBackendConnectionObject = EmailBackend()

        modelClass_CorrespondingReportHelper_Mappings = [
            {
                MODEL_CLASS_KEY_STRING: models.DailyAircraftMovementsBangalore,
                # REPORT_HELPER_FUNCTION_KEY_STRING: dailyAircraftMovementsBangaloreHelper
                REPORT_HELPER_FUNCTION_KEY_STRING: DailyAircraftMovementsBangaloreHelper.dailyAircraftMovementsBangaloreHelper
            },
            {
                MODEL_CLASS_KEY_STRING: models.DailyAircraftMovementsChennai,
                REPORT_HELPER_FUNCTION_KEY_STRING: DailyAircraftMovementsChennaiHelper.dailyAircraftMovementsChennaiHelper
            },
            {
                MODEL_CLASS_KEY_STRING: models.DailyAircraftMovementsDelhi,
                REPORT_HELPER_FUNCTION_KEY_STRING: DailyAircraftMovementsDelhiHelper.dailyAircraftMovementsDelhiHelper
            },
            {
                MODEL_CLASS_KEY_STRING: models.DailyAircraftMovementsKolkata,
                REPORT_HELPER_FUNCTION_KEY_STRING: DailyAircraftMovementsKolkataHelper.dailyAircraftMovementsKolkataHelper
            },
            {
                MODEL_CLASS_KEY_STRING: models.DailyAircraftMovementsMumbai,
                REPORT_HELPER_FUNCTION_KEY_STRING: DailyAircraftMovementsMumbaiHelper.dailyAircraftMovementsMumbaiHelper
            },
        ]
        

        mostRecentEmailLog = models.DailyAircraftMovementsEmailLogs.objects.order_by('-utcDate').first()
        if mostRecentEmailLog is None:
            """
            When no email has ever been sent, we will assume yesterday to be the first day for which email has to be sent.
            To facilitate this, we'll set dateTillWhichEmailsSent to 2 days back.
            """
            dateTillWhichEmailsSent = timezone.now().date() - datetime.timedelta(days=2)
        else:
            dateTillWhichEmailsSent = mostRecentEmailLog.utcDate
            
        # Send email for each intervening day.
        while (dateTillWhichEmailsSent < yesterddayDate):
            dateUnderConsideration = dateTillWhichEmailsSent + datetime.timedelta(days=1)
            reportBufferObject_Filename_Mappings_List = []  # will store BytesIO buffer objects (as retrieved from ReportGenerationHelpers), along with their appropriate filenames.
            failedModelNamesList = []                       # will store the names of models for which report generation failed.
            for modelClass_CorrespondingReportHelper_Mapping in modelClass_CorrespondingReportHelper_Mappings:
                modelClass = modelClass_CorrespondingReportHelper_Mapping[MODEL_CLASS_KEY_STRING]
                countOfDailyAircraftMovementsObjects = modelClass.objects.filter(utcDate = dateUnderConsideration).count()
                if countOfDailyAircraftMovementsObjects > 0:
                    reportHelper = modelClass_CorrespondingReportHelper_Mapping[REPORT_HELPER_FUNCTION_KEY_STRING]
                    buffer = reportHelper(utcDate = dateUnderConsideration)
                    reportBufferObject_Filename_Mappings_List.append(
                        {
                            BUFFER_OBJECT_KEY_STRING: buffer,
                            FILE_NAME_KEY_STRING: modelClass._meta.verbose_name + " - " + dateUnderConsideration.strftime("%Y-%m-%d") + ".xlsx"
                        }
                    )
                else:
                    failedModelNamesList.append(modelClass._meta.verbose_name)
            if len(failedModelNamesList) == 0:
                """[CASE-1:] Report generation was successful for all airports. Send email to DGCA and other intended recipients."""
                subject = "Daily Aircraft Movement Reports - " + dateUnderConsideration.strftime("%d-%b-%Y") + "."
                body = "Daily Aircraft Movement Reports - " + dateUnderConsideration.strftime("%d-%b-%Y") + "."
                emailRecipients = [emailRecipient.email for emailRecipient in models.DailyAircraftMovementsEmailRecipients.objects.all()]
                emailObject = EmailMessage(
                    subject = subject, 
                    body = body, 
                    to = emailRecipients,
                    connection=smtpBackendConnectionObject)
                for reportBufferObject_Filename_Mapping in reportBufferObject_Filename_Mappings_List:
                    fileName = reportBufferObject_Filename_Mapping[FILE_NAME_KEY_STRING]
                    attachment = reportBufferObject_Filename_Mapping[BUFFER_OBJECT_KEY_STRING].getvalue()
                    emailObject.attach(filename=fileName, content=attachment)
                try:
                    # 1. Send email to the intended recipients.
                    emailSentFlag = emailObject.send()
                    # 2. If email sent successfully, log it.
                    if emailSentFlag:
                        # 2.1. Update the logs.
                        dailyAircraftMovementsEmailLogsObject = models.DailyAircraftMovementsEmailLogs()
                        dailyAircraftMovementsEmailLogsObject.utcDate = dateUnderConsideration
                        dailyAircraftMovementsEmailLogsObject.loggedMessage = "Successfully sent email to " + ", ".join(emailRecipients) + "."
                        setDefaultCreatedByModifiedByUsers(dailyAircraftMovementsEmailLogsObject)
                        dailyAircraftMovementsEmailLogsObject.save()
                        # 2.2. Update the dateTillWhichEmailsSent.
                        dateTillWhichEmailsSent = dateUnderConsideration
                    # 3. If email coudln't be sent, raise exception
                    else:
                        raise Exception("Failed to send email bearing subject: " + subject + ".")
                except Exception as e:
                    note = """Failed to send email with subject: """ + subject + """ to recipients: """ + str(emailRecipients)
                    e.add_note(note)
                    raise e
            else:
                if timezone.now().time() < UPPER_TIME_LIMIT:
                    """[CASE-2:] Report generation was unsuccessful for some/all airports. If we are yet to hit the upper time limit (UPPER_TIME_LIMIT), send email to Failure Recipients. We will wait for 1 hour after which, we'll re-check for this date."""
                    subject = "Daily Aircraft Movement Reports - " + dateUnderConsideration.strftime("%d-%b-%Y") + " - REPORT GENERATION FAILURE - REMINDER NOTICE."
                    body = "The Daily Aircraft Movement Reports - " + dateUnderConsideration.strftime("%d-%b-%Y") + " failed for the following datasets: " + ", ".join(failedModelNamesList) + "."
                    emailRecipients = [emailRecipient.email for emailRecipient in models.DailyAircraftMovementsEmailFailureRecipients.objects.all()]
                    emailObject = EmailMessage(
                        subject = subject, 
                        body = body, 
                        to = emailRecipients,
                        connection=smtpBackendConnectionObject)
                    try:
                        # Since data for this date is yet to be entered by the authoritized users, send email alert to FailureRecipientsa and sleep for 1 hour after which, you'll re-check for this date.
                        emailSentFlag = emailObject.send()
                        if not emailSentFlag:
                            raise Exception("Failed to send email bearing subject: " + subject + ".")
                    except Exception as e:
                        note = """Failed to send email with subject: """ + subject + """ to recipients: """ + str(emailRecipients)
                        e.add_note(note)
                        raise
                    time.sleep(3600)    # make the process sleep for 1 hour after which you'll re-check for this date.
                    # time.sleep(5)    # # This shorter sleep is for testing purposes. Comment the above line before using this.
                else:
                    """[CASE-3:] Report generation was unsuccessful for some/all airports. If we are past the upper time limit (UPPER_TIME_LIMIT), send email to DGCA and other intended recipients, mentioning the datasets (models) for which data coudln't be found."""
                    # Beyond the upper time limit, send email to the intended recipients, mentioning the datasets (models) for which data coudln't be found.
                    subject = "Daily Aircraft Movement Reports - " + dateUnderConsideration.strftime("%d-%b-%Y") + " - REPORT GENERATION FAILURE - FINAL NOTIFICATION."
                    body = "The Daily Aircraft Movement Reports - " + dateUnderConsideration.strftime("%d-%b-%Y") + " failed for the following datasets: \n" + "\n".join(failedModelNamesList) + "."
                    emailRecipients = [emailRecipient.email for emailRecipient in models.DailyAircraftMovementsEmailRecipients.objects.all()]
                    emailObject = EmailMessage(
                        subject = subject, 
                        body = body, 
                        to = emailRecipients,
                        connection=smtpBackendConnectionObject)
                    for reportBufferObject_Filename_Mapping in reportBufferObject_Filename_Mappings_List:
                        fileName = reportBufferObject_Filename_Mapping[FILE_NAME_KEY_STRING]
                        attachment = reportBufferObject_Filename_Mapping[BUFFER_OBJECT_KEY_STRING].getvalue()
                        emailObject.attach(filename=fileName, content=attachment)
                    try:
                        # 1. Send email to the intended recipients.
                        emailSentFlag = emailObject.send()
                        # 2. If email sent successfully, log it.
                        if emailSentFlag:
                            # 2.1. Update the logs.
                            dailyAircraftMovementsEmailLogsObject = models.DailyAircraftMovementsEmailLogs()
                            dailyAircraftMovementsEmailLogsObject.utcDate = dateUnderConsideration
                            dailyAircraftMovementsEmailLogsObject.loggedMessage = body + "Successfully sent aforementioned email to " + ", ".join(emailRecipients) + "."
                            setDefaultCreatedByModifiedByUsers(dailyAircraftMovementsEmailLogsObject)
                            dailyAircraftMovementsEmailLogsObject.save()
                            # 2.2. Update the dateTillWhichEmailsSent.
                            dateTillWhichEmailsSent = dateUnderConsideration
                        # 3. If email coudln't be sent, raise exception
                        else:
                            raise Exception("Failed to send email bearing subject: " + subject + ".")
                    except Exception as e:
                        note = """Failed to send email with subject: """ + subject + """ to recipients: """ + str(emailRecipients)
                        e.add_note(note)
                        raise
                    
