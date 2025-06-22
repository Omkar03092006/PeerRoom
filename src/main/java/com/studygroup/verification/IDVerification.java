package com.studygroup.verification;

import java.io.File;

public class IDVerification {
    public static void main(String[] args) {
        if (args.length < 1) {
            System.out.println("Please provide the path to the ID card image.");
            return;
        }

        String imagePath = args[0];
        File imageFile = new File(imagePath);
        
        if (!imageFile.exists()) {
            System.err.println("Error: Image file does not exist: " + imagePath);
            return;
        }

        // Initialize verifier with the tessdata directory (should be in project root)
        BennettIDVerifier verifier = new BennettIDVerifier("tessdata");

        try {
            VerificationResult result = verifier.verifyIDCard(imageFile);
            System.out.println("Verification Result:");
            System.out.println("Success: " + result.isSuccess());
            System.out.println("Message: " + result.getMessage());
            if (result.getEnrollmentNumber() != null) {
                System.out.println("Enrollment Number: " + result.getEnrollmentNumber());
            }
            if (result.getStudentName() != null) {
                System.out.println("Student Name: " + result.getStudentName());
            }
        } catch (Exception e) {
            System.err.println("Error during verification: " + e.getMessage());
            e.printStackTrace();
        }
    }
} 