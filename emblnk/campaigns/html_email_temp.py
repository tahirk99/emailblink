test_mail_content = '''
<!DOCTYPE html>
<html>
<head>
    <style>
        /* Add some basic styles for the email */
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }

        h1 {
            color: #007BFF;
        }

        p {
            color: #333;
        }

        /* Define styles for the personalized and random sections */
        .personalized {
            font-weight: bold;
        }

        .icons {
            font-size: 24px;
        }

        .random-content {
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Hello, <span class="personalized">%first_name%</span>!</h1>
        <p>Welcome to <span class="personalized">%company%</span>. We're excited to have you on board.</p>

        <p>Here %dob%||are some random icons: <span class="icons">⭐️ 🌟 ✉️ 📆 📎 📝 📊</span></p>
        
        <p class="random-content">This is %subscribed%||Yes Subscribed% some random testing content for your email. You can replace this with any specific message you'd like to convey.</p>

        <p>Thank you for being a part of our community.</p>

        <p><a href="https://digiholix.com/">Digiholix website</a>
        <p><a href="https://digiholix.com/contact-us">Contact us page</a>

        <p>Sincerely,<br>Your Company</p>
        <br>
        <a href="%UNSUBSCRIBE%">Unsubscribe</a>
    </div>
</body>
</html>
'''