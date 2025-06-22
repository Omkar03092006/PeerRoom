package com.studygroup.verification;

import java.io.File;

public class IDVerificationTest {
    public static void main(String[] args) {
        // Initialize the verifier
        BennettIDVerifier verifier = new BennettIDVerifier("tessdata");
        
        // Get the image path from command line arguments
        String imagePath = args.length > 0 ? args[0] : "sample_id.jpg";
        File idCardImage = new File(imagePath);
        
        if (!idCardImage.exists()) {
            System.out.println("Error: ID card image not found at path: " + imagePath);
            return;
        }
        
        // Perform verification
        VerificationResult result = verifier.verifyIDCard(idCardImage);
        
        // Print results
        System.out.println("Verification Result:");
        System.out.println("Success: " + result.isSuccess());
        System.out.println("Message: " + result.getMessage());
        
        if (result.isSuccess()) {
            System.out.println("Student Name: " + result.getStudentName());
            System.out.println("Enrollment Number: " + result.getEnrollmentNumber());
        }
    }
} 