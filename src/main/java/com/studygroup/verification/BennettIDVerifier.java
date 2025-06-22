package com.studygroup.verification;

import java.io.File;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import net.sourceforge.tess4j.Tesseract;
import net.sourceforge.tess4j.TesseractException;

public class BennettIDVerifier {
    private final Tesseract tesseract;
    private static final Pattern ENROLLMENT_PATTERN = Pattern.compile("E\\d{8}");
    private static final Pattern NAME_PATTERN = Pattern.compile("Name:\\s*([A-Za-z\\s]+)");

    public BennettIDVerifier(String dataPath) {
        this.tesseract = new Tesseract();
        this.tesseract.setDatapath(dataPath);
        this.tesseract.setLanguage("eng");
    }

    public VerificationResult verifyIDCard(File imageFile) {
        try {
            String extractedText = tesseract.doOCR(imageFile);
            
            // Extract enrollment number
            Matcher enrollmentMatcher = ENROLLMENT_PATTERN.matcher(extractedText);
            String enrollmentNumber = enrollmentMatcher.find() ? enrollmentMatcher.group() : null;

            // Extract student name
            Matcher nameMatcher = NAME_PATTERN.matcher(extractedText);
            String studentName = nameMatcher.find() ? nameMatcher.group(1).trim() : null;

            if (enrollmentNumber != null && studentName != null) {
                return new VerificationResult(true, "ID card verified successfully", 
                                           enrollmentNumber, studentName);
            } else {
                return new VerificationResult(false, 
                    "Could not extract required information from ID card", null, null);
            }
        } catch (TesseractException e) {
            return new VerificationResult(false, 
                "Error processing ID card: " + e.getMessage(), null, null);
        }
    }
}