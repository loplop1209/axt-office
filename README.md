# AXT Office — GitHub APK Build

این پروژه برای ساخت APK نسخه Kivy برنامه AXT Office با GitHub Actions آماده شده است.

## ساخت APK

1. این پوشه را در یک GitHub Repository آپلود کن.
2. وارد تب **Actions** شو.
3. Workflow با نام **Build AXT Office APK** را انتخاب کن.
4. روی **Run workflow** بزن.
5. پس از پایان Build، در صفحه اجرای Workflow بخش **Artifacts** را باز کن.
6. فایل `AXT-Office-APK` را دانلود کن و APK داخل آن را روی گوشی نصب کن.

Workflow فایل `AXT_Office_Kivy.py` را به `main.py` تبدیل می‌کند؛ بنابراین لازم نیست نام فایل اصلی را دستی تغییر بدهی.

نکته: این Build نسخه debug است. برای انتشار در Google Play باید نسخه release/AAB و signing جداگانه تنظیم شود.
