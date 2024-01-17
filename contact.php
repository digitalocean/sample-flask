<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $firstName = $_POST["firstName"];
    $lastName = $_POST["lastName"];
    $email = $_POST["email"];
    $reference = $POST["reference"];
    $message = $_POST["message"];

    $to = "yelena@bohemethreads.com";
    $subject = "New Contact Form Submission";
    $headers = "From: $email";


    $success = mail($to, $subject, $message, $headers);

    if ($success) {
        echo "Thank you for contacting us!";
    } else {
        echo "Sorry, there was an error sending your message. Please try again later.";
    }
}
?>