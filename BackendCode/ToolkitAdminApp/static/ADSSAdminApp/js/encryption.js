const {pubilcEncrypt, privateDecrypt} = require('crypto');
function encrypt(publicKey)
{
    let password = document.getElementsByName('password')[0].value;
    let otp = document.getElementsByName('otp')[0].value;
    if(password)
    {
        document.getElementsByName('password')[0].value = pubilcEncrypt(publicKey, password);
    }
    if(otp)
    {
        document.getElementsByName('otp')[0].value = pubilcEncrypt(publicKey, otp);
    }
    return true;
}