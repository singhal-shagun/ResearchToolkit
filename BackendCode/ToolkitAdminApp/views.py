from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.views import LoginView
from InfrastructureApp.views.generic.edit import InfrastructureFormView
from InfrastructureApp.views.generic.base import InfrastructureRedirectView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from .forms import LoginForm, LoginOTPUsageForm, PasswordResetForm, PasswordResetOTPUsageForm
from django.contrib.auth import get_user_model, logout
from django.core.mail import send_mail
from django.urls import reverse, reverse_lazy
from .models import LoginOTPs, PasswordResetOTPs
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from smtplib import SMTPException
from django.http import QueryDict, HttpResponseRedirect
from InfrastructureApp.constants import HTTPMethods
from InfrastructureApp.admin import ToolkitAdminSite
from InfrastructureApp.EncryptionUtility import setEncryptionKeyPairInSession, deleteEncryptionKeyPairFromSessionForAuthenticatedUsers



# Create your views here.
class AdminLoginRedirectView(PermissionRequiredMixin, InfrastructureRedirectView):

    # 1. Define the permissions required for this view.
    permission_required = []    # Without the LoginRequiredMixin, empty permission_required list allows even unauthenticated users to view the View.

    # 2. Define the view title.
    title = "Redirect to Login Page"

    # 3. Define the URL to be redirected to.
    # url = reverse_lazy("ToolkitAdminApp.ToolkitLoginView")
    pattern_name = "ToolkitAdminApp.ToolkitLoginView" # django will reverse this pattern in this RedirectView's get_redirect_url() method.

    # 4. Allowed HTTP methods.
    http_method_names = [HTTPMethods.get,]


    ###########
    ### RedirectView class' methods.
    ###########
    def get_redirect_url(self, *args, **kwargs):
        url = super().get_redirect_url(*args, **kwargs)

        # create a QueryDict object with 'next' parameter.
        query = QueryDict(mutable=True)
        # query['next'] = reverse_lazy('AdministrationSide')    # For some reason, this didn't work.
        query['next'] = '/admin/'

        # append the QueryDict object to the URL.
        url = url + '?' + query.urlencode()

        return url


class ToolkitLoginView(PermissionRequiredMixin, LoginView):

    # 1. Define the permissions required for this view.
    permission_required = []    # Without the LoginRequiredMixin, empty permission_required list allows even unauthenticated users to view the View.

    # 2. Define the view title.
    title = "Login"
    
    # 3. Define the template.
    template_name = "ToolkitAdminApp/login.html"

    # 4. Define the URL to redirect to after login.
    # This isn't necessitated by the default django LoginView.
    # However, to incorporate 2-factor authentication for elevated users (superusers) as per ISMS team's recommendation, we'll set this in form_valid().
    # success_url = None

    # 5. Override the login form.
    form_class = LoginForm

    # 6. Allowed HTTP methods.
    http_method_names = [HTTPMethods.get, HTTPMethods.post, ]

    
    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)

       if self.request.user.is_anonymous:
            # Generate the public-private key-pair for RSA encryption-decyption of user password.
            # [NOTE:] we store the encryption keys in database as part of user session. 
            # They'll be deleted from session data in the database after decrypting the user password, if the user is authenticated successfully. 
            # (See post() for code where these keys are deleted.)
            setEncryptionKeyPairInSession(self.request)
       return context
    
    
    def form_valid(self, form):
        if settings.DEBUG:
            # We don't want the complicated production environment logic in development environment.
            return super().form_valid(form)
        """
        As per django's LoginView, this method is called when the security check is complete from a password authentication point-of-view.
        Now, we'll go for 2nd factor authentication.
        As per AAI's ISMS team, 2-factor authentication involves:
            1. A static code (in our case, the password);
            2 A variable code (in our case, we'll send an OTP via email).
        """
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        allowLoginBoolean = True

        """
        Step-1: Check if the user exists in the database. Also check if the password is correct.
        If either condition isn't met, let LoginView handle this login attempt on its own. (This case is never executed because LoginView's form handles this case on its own..)
        If it does, proceed to step-2.
        """
        # Check-1: Check if the user exists in the database.
        try:
            userObject = get_user_model().objects.get(username=username)
        except ObjectDoesNotExist:
            allowLoginBoolean = False
        # Check-2: Check if the password is correct.
        if not userObject.check_password(password):
            allowLoginBoolean = False
        # If either condition isn't met, let LoginView handle this login attempt on its own.
        if not allowLoginBoolean:
            # messages.error(self.request, "Invalid username or password.")
            return super().form_valid(form)
        
        """
        Step-2: Check if the user is a superuser.
        If not, let the default LoginView handle this login attempt on its own.
        Else, for superuser login, proceed to step-3 for pre-checks i.r.o. 2-factor authentication.
        """
        # [2023-09-20:] This condition has been commented. Now, 2-factor authentication has been made mandatory for all users to avoid the costs of CAPTCHA API.
        # if not userObject.is_superuser:
        #     # return super().form_valid(form)
        #     response = super().form_valid(form)
        #     return response
        
        """
        Step-3: Pre-checks for superuser login: 
            1. Check if the user has an associated email.
            2. Check if the user has not already requested a Login OTP within the past 1 minute.
        [2023-09-20:] Since the aforementioned superuser condition check has been commented, now,the checks in this section are performed for all users.
        """
        allowLoginBoolean = True
        # Check-1: Check if the user has an associated email.
        if ((userObject.email == "") or (userObject.email is None)):
            allowLoginBoolean = False
            messages.error(self.request, "No email associated with this account.")

            # method-1: Works, but doesn't maintain form data.
            # self.success_url = reverse_lazy("ToolkitAdminApp.ToolkitLoginView")
            # return HttpResponseRedirect(self.get_success_url())

            # method-2: Works, but doesn't maintain form data either.
            # return HttpResponseRedirect(self.request.get_full_path())

            # method-3: Works. Also maintains form data.

        # Check-2: Rate Limiting: Prevent repeated Login OTP requests if this superuser had already made a login attempt within the past 1 minute.
        # Allow this code block execution only if the user has not already been denied a login attempt.
        if allowLoginBoolean:
            try:
                loginOTPModelInstance = LoginOTPs.objects.get(referencedUser_id = userObject.id)
                timeDelta = timezone.now() - loginOTPModelInstance.dbEntryCreationDateTime
                if timeDelta.total_seconds() < 60:
                    messages.add_message(self.request,
                                        messages.ERROR,
                                        "Please wait at least 1 minute before making another login attempt.")
                    allowLoginBoolean = False
            except ObjectDoesNotExist:
                # User has no prior Login OTP. All good.
                pass
        
        # If either of the above checks wants to prevent login attempt, call form_invalid().
        if not allowLoginBoolean:
            return self.form_invalid(form=form)
        
        """
        Step-4: Proceed for 2-factor authentication for superuser login.
        """
        self.success_url = reverse_lazy("ToolkitAdminApp.ToolkitLoginOTPUsageView")
        try:
            loginOTPsModelInstance = LoginOTPs()
            loginOTPsModelInstance.referencedUser_id = userObject.id
            loginOTPsModelInstance.createdBy = userObject
            loginOTPsModelInstance.modifiedBy = userObject
            #loginOTPsModelInstance.full_clean()
            loginOTPsModelInstance.save()

            try:
                emailBody = "\n".join([
                    str("Username: " + userObject.username),
                    str("One-Time Password: " + loginOTPsModelInstance.otp),
                    str("Validity till: " + loginOTPsModelInstance.validTillDateTime.strftime("%d %b %Y, %H:%M:%S") + " (UTC datetime in 24-Hour format)"),
                    str("To use this One-Time Password, visit: " + self.request.build_absolute_uri(self.success_url)),
                    ])
                sentEmailCount = send_mail(
                                    subject = "Login Email - " + ToolkitAdminSite.site_title,
                                    message = emailBody,
                                    from_email = None,
                                    recipient_list = [userObject.email,],
                                    fail_silently=False,
                                )
                if sentEmailCount > 0:
                    m = "Login OTP sent to the associated email account."
                    messages.add_message(self.request,
                                            messages.SUCCESS,
                                            m)
            except SMTPException as e:
                loginOTPsModelInstance.delete()
                raise Exception(e.args[0][userObject.email])
        except Exception as e:
            if hasattr(e, "messages"):
                for m in e.messages:
                    messages.add_message(self.request,
                                            messages.ERROR,
                                            m)
            else:
                for arg in e.args:
                    messages.add_message(self.request,
                                            messages.ERROR,
                                            arg)
            return self.form_invalid(form=form)
        else:
            response  = HttpResponseRedirect(self.get_success_url())
            # response['username'] = userObject.username
            self.request.session['username'] = userObject.username
            return response
    
    
    def form_invalid(self, form):
        return super().form_invalid(form)
        

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        response = super().post(request, *args, **kwargs)

        # If the user has been authenticated, delete the key-pair used to encrypt user credentials.
        deleteEncryptionKeyPairFromSessionForAuthenticatedUsers(request)

        return response
    
    
    def get_success_url(self):
        success_url = self.success_url or super().get_success_url()
        next_url = self.request.GET.get('next') or self.request.POST.get('next') 
        if next_url:
            return f"{success_url}?next={next_url}"
        else:
            return success_url

    # def get_redirect_url(self):
    #     return str(self.success_url) or super().get_redirect_url()  # success_url may be lazy


class ToolkitLoginOTPUsageView(PermissionRequiredMixin, LoginView):

    # 1. Define the permissions required for this view.
    permission_required = []    # Without the LoginRequiredMixin, empty permission_required list allows even unauthenticated users to view the View.

    # 2. Define the view title.
    title = "Login OTP"
    
    # 3. Define the template.
    template_name = "ToolkitAdminApp/loginOTPUsage.html"

    # 4. Form class.
    form_class = LoginOTPUsageForm

    # 5. Success URL.
    success_url = None

    # 6. Allowed HTTP methods.
    http_method_names = [HTTPMethods.get, HTTPMethods.post, ]


    ##########
    ### FormView class' methods.
    ##########
    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)

    #    if self.request.user.is_anonymous and (self.request.method.lower() == HTTPMethods.get):
       if self.request.user.is_anonymous:
            # Generate the public-private key-pair for RSA encryption-decyption of user password.
            # [NOTE:] we store the encryption keys in database as part of user session. 
            # They'll be deleted from session data in the database after decrypting the user password, if the user is authenticated successfully. 
            # (See post() for code where these keys are deleted.)
            setEncryptionKeyPairInSession(self.request)
       return context

    
    def get_initial(self):
        copyOfInitial = super().get_initial()
        if 'username' in self.request.session:
            copyOfInitial['username'] = self.request.session['username']
        return copyOfInitial


    def form_valid(self, form):
        username = form.cleaned_data["username"]
        password = form.cleaned_data.get("password")
        otp = form.cleaned_data["otp"]

        """
        Step-1: Check if the user exists in the database.
        If it doesn't let the default LoginView handle this login attempt on its own.
        """
        try:
            userObject = get_user_model().objects.get(username = username)
        except ObjectDoesNotExist:
            super().form_valid(form)

        """
        Step-2: Check if the OTP matches with any OTP in the database for this user.
        ALso confirm that the OTP hasn't expired. If it's expired, redirect to the Login page.
        """
        # 1. Check if the OTP matches with any OTP in the database for this user.
        try:
            loginOTPObject = LoginOTPs.objects.get(
                referencedUser_id = userObject.id,
                otp = otp
                )
        except ObjectDoesNotExist:
            messages.add_message(self.request,
                                    messages.ERROR,
                                    "Incorrect OTP.")
            return self.form_invalid(form=form)
        # 2. Confirm that the OTP hasn't expired.
        if (timezone.now() > loginOTPObject.validTillDateTime):
            messages.add_message(self.request,
                                    messages.ERROR,
                                    "OTP expired. Please restart your loging attempt.")
            self.success_url = reverse_lazy("ToolkitAdminApp.ToolkitLoginView")
            response  = HttpResponseRedirect(self.get_success_url())
            response['next'] = self.request.POST.get("next")
            return response
        
        """
        Step-3: Attempt user login. If the login is successul, delete the OTP from the database
        """
        # 1. Attempts login.
        response = super().form_valid(form)
        response['next'] = self.request.POST.get("next")

        # 2. If login was unsuccessful, username would now become available in the request object.
        if self.request.user.username == username:
            loginOTPObject.delete()

        return response


    def form_invalid(self, form):
        return super().form_invalid(form)
    

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        response = super().post(request, *args, **kwargs)

        # If the user has been authenticated, delete the key-pair used to encrypt user credentials.
        deleteEncryptionKeyPairFromSessionForAuthenticatedUsers(request)

        return response
    
    
    def get_success_url(self):
        success_url = self.success_url or super().get_success_url()
        next_url = self.request.GET.get('next') or self.request.POST.get('next') 
        if next_url:
            return f"{success_url}?next={next_url}"
        else:
            return success_url


class ToolkitPasswordResetView(PermissionRequiredMixin, InfrastructureFormView):

    # 1. Define the permissions required for this view.
    permission_required = []    # Without the LoginRequiredMixin, empty permission_required list allows even unauthenticated users to view the View.

    # 2. Define the view title.
    title = "Reset Password"
    
    # 3. Define the template.
    template_name = "ToolkitAdminApp/PasswordResetForm.html"
    
    # 4. Define the form_class (for FormView classes).
    form_class = PasswordResetForm

    # 5. Success URL.
    success_url = reverse_lazy("ToolkitAdminApp.PasswordResetOTPUsageView")

    # 6. Allowed HTTP methods.
    http_method_names = [HTTPMethods.get, HTTPMethods.post, ]


    ##########
    ### FormView class' methods.
    ##########
    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)

       if self.request.user.is_anonymous:
            # Generate the public-private key-pair for RSA encryption-decyption of user password.
            # [NOTE:] we store the encryption keys in database as part of user session. 
            # They'll be deleted from session data in the database after decrypting the username, if password reset OTP has been sent. 
            # (See post() for code where these keys are deleted.)
            setEncryptionKeyPairInSession(self.request)
       return context

    def form_valid(self, form):
        try:
            #self.success_url = reverse_lazy("ToolkitAdminApp.ToolkitPasswordResetView")  # This technique works. But not required here.
            user = get_user_model().objects.get(username = form.cleaned_data["username"])
            if ((user.email == "") or (user.email is None)):
                messages.add_message(self.request,
                                        messages.ERROR,
                                        "No email associated with this account.")
        except ObjectDoesNotExist as e:
            messages.add_message(self.request,
                                    messages.ERROR,
                                    "Password cannot be reset.")
        messagesStorage = messages.get_messages(self.request)
        if (len(messagesStorage) > 0 ):
            self.success_url = reverse_lazy("ToolkitAdminApp.ToolkitPasswordResetView")
            return super().form_valid(form)
        try:
            if user is not None:
                # Rate Limiting: Prevent repeated password reset requests if the user has already requested a password reset within the past 1 minute.
                try:
                    passwordResetOTPModelInstance = PasswordResetOTPs.objects.get(referencedUser_id = user.id)
                    timeDelta = timezone.now() - passwordResetOTPModelInstance.dbEntryCreationDateTime
                    if timeDelta.total_seconds() < 60:
                        messages.add_message(self.request,
                                            messages.ERROR,
                                            "Please wait at least 1 minute before submitting another password reset request.")
                        return self.form_invalid(form)
                except ObjectDoesNotExist:
                    # All good. Proceed with password reset.
                    pass

                passwordResetOTPModelInstance = PasswordResetOTPs()
                passwordResetOTPModelInstance.referencedUser_id = user.id
                passwordResetOTPModelInstance.createdBy = user
                passwordResetOTPModelInstance.modifiedBy = user
                #passwordResetOTPModelInstance.full_clean()
                passwordResetOTPModelInstance.save()

                try:
                    emailBody = "\n".join([
                        str("Username: " + user.username),
                        str("One-Time Password: " + passwordResetOTPModelInstance.otp),
                        str("Validity till: " + passwordResetOTPModelInstance.validTillDateTime.strftime("%d %b %Y, %H:%M:%S") + " (UTC datetime in 24-Hour format)"),
                        str("To use this One-Time Password, visit: " + self.request.build_absolute_uri(self.success_url)),
                        ])
                    sentEmailCount = send_mail(
                                        subject = "Password Reset Email - " + ToolkitAdminSite.site_title,
                                        message = emailBody,
                                        from_email = None,
                                        recipient_list = [user.email,],
                                        fail_silently=False,
                                    )
                    if sentEmailCount > 0:
                        m = "New password sent to the associated email account."
                        messages.add_message(self.request,
                                                messages.SUCCESS,
                                                m)
                except SMTPException as e:
                    passwordResetOTPModelInstance.delete()
                    raise Exception(e.args[0][user.email])
        except Exception as e:
            if hasattr(e, "messages"):
                for m in e.messages:
                    messages.add_message(self.request,
                                            messages.ERROR,
                                            m)
            else:
                for arg in e.args:
                    messages.add_message(self.request,
                                            messages.ERROR,
                                            arg)
        return super().form_valid(form)


    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response
        

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        response = super().post(request, *args, **kwargs)

        # If password reset OTP has been sent, delete the key-pair used to encrypt user credentials.
        deleteEncryptionKeyPairFromSessionForAuthenticatedUsers(request)

        return response
    
    
    def get_success_url(self):
        success_url = self.success_url or super().get_success_url()
        next_url = self.request.GET.get('next') or self.request.POST.get('next') 
        if next_url:
            return f"{success_url}?next={next_url}"
        else:
            return success_url


class PasswordResetOTPUsageView(PermissionRequiredMixin, InfrastructureFormView):

    # 1. Define the permissions required for this view.
    permission_required = []    # Without the LoginRequiredMixin, empty permission_required list allows even unauthenticated users to view the View.

    # 2. Define the view title.
    title = "Password Reset OTP Sent"
    
    # 3. Define the template.
    template_name = "ToolkitAdminApp/PasswordResetOTPUsageForm.html"
    
    # 4. Define the form_class (for FormView classes).
    form_class = PasswordResetOTPUsageForm

    # 5. Success URL.
    success_url = reverse_lazy("ToolkitAdminApp.ToolkitPasswordResetView")

    # 6. Allowed HTTP methods.
    http_method_names = [HTTPMethods.get, HTTPMethods.post, ]


    ##########
    ### FormView class' methods.
    ##########
    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)

       if self.request.user.is_anonymous:
            # Generate the public-private key-pair for RSA encryption-decyption of user password.
            # [NOTE:] we store the encryption keys in database as part of user session. 
            # They'll be deleted from session data in the database after decrypting the username & otp. 
            # (See post() for code where these keys are deleted.)
            setEncryptionKeyPairInSession(self.request)
       return context

    def form_valid(self, form):
        try:
            username = form.cleaned_data["username"]
            otp = form.cleaned_data["otp"]
            user = get_user_model().objects.get(username = username)
            passwordResetOTPModelInstance = PasswordResetOTPs.objects.get(
                referencedUser_id = user.id,
                otp = otp
                )
            if (timezone.now() > passwordResetOTPModelInstance.validTillDateTime):
                messages.add_message(self.request,
                                        messages.ERROR,
                                        "One-Time Password expired. Please regenerate the One-Time Password.")
                return super().form_valid(form)

            user.set_password(otp)
            user.full_clean()
            user.save()
            passwordResetOTPModelInstance.delete()
            messages.add_message(self.request,
                                    messages.SUCCESS,
                                    "Password changed to the OTP. Please login using the OTP as your new password.")
            self.success_url = reverse_lazy("ToolkitAdminApp.ToolkitLoginView")
            return super().form_valid(form)

        except ObjectDoesNotExist:
            messages.add_message(self.request,
                                 messages.ERROR,
                                 "Password cannot be reset.")
        except Exception as e:
            if hasattr(e, "messages"):
                for m in e.messages:
                    messages.add_message(self.request,
                                            messages.ERROR,
                                            m)
            else:
                for arg in e.args:
                    messages.add_message(self.request,
                                            messages.ERROR,
                                            arg)
        return super().form_valid(form)


    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response
        

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        response = super().post(request, *args, **kwargs)

        # If password reset OTP verification is complete, delete the key-pair used to encrypt user credentials.
        deleteEncryptionKeyPairFromSessionForAuthenticatedUsers(request)

        return response
    
    
    def get_success_url(self):
        success_url = self.success_url or super().get_success_url()
        next_url = self.request.GET.get('next') or self.request.POST.get('next') 
        if next_url:
            return f"{success_url}?next={next_url}"
        else:
            return success_url


class ToolkitLogoutView(LoginRequiredMixin, PermissionRequiredMixin, InfrastructureRedirectView):

    # 1. Define the permissions required for this view.
    permission_required = []    # Without the LoginRequiredMixin, empty permission_required list allows even unauthenticated users to view the View.

    # 2. Define the view title.
    title = "Log out"

    # 3. Allowed HTTP methods.
    http_method_names = [HTTPMethods.get, ]

    # 4. Set the redirect URL.
    url = reverse_lazy(settings.LOGOUT_REDIRECT_URL)

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)