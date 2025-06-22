package com.studygroup.verification;

import java.io.File;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import net.sourceforge.tess4j.Tesseract;
import net.sourceforge.tess4j.TesseractException;

public class PythonIDVerifier {
    private final Tesseract tesseract;
    private static final Pattern ENROLLMENT_PATTERN = Pattern.compile("S\\d{2}CSEU\\d{4}");
    private static final Gson gson = new GsonBuilder().setPrettyPrinting().create();

    public PythonIDVerifier(String dataPath) {
        this.tesseract = new Tesseract();
        this.tesseract.setDatapath(dataPath);
        this.tesseract.setLanguage("eng");
        
        // Configure Tesseract for better accuracy
        this.tesseract.setPageSegMode(6); // Assume uniform text block
        this.tesseract.setOcrEngineMode(1); // Legacy + LSTM for better accuracy
        
        // Enhanced image processing configuration
        this.tesseract.setTessVariable("tessedit_char_whitelist", "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .-");
        this.tesseract.setTessVariable("textord_heavy_nr", "1"); // Reduce noise
        this.tesseract.setTessVariable("tessedit_pageseg_mode", "6");
        this.tesseract.setTessVariable("tessedit_do_invert", "0");
        this.tesseract.setTessVariable("debug_file", "/dev/null");
        this.tesseract.setTessVariable("tessedit_write_images", "1");
    }

    private String findNameInText(String extractedText, String registeredName) {
        System.err.println("\n=== Starting name search ===");
        System.err.println("Looking for registered name: '" + registeredName + "'");
        
        // Preprocess the extracted text
        String processedText = extractedText.toLowerCase()
            .replaceAll("[^a-z0-9\\s.-]", "") // Remove any special characters
            .replaceAll("\\s+", " ")
            .trim();
        
        // Preprocess the registered name
        String processedName = registeredName.toLowerCase()
            .replaceAll("[^a-z0-9\\s.-]", "")
            .replaceAll("\\s+", " ")
            .trim();
        
        System.err.println("Processed extracted text:\n" + processedText);
        System.err.println("Processed name to find: " + processedName);
        
        // First try exact match
        if (processedText.contains(processedName)) {
            System.err.println("Found exact name match");
            return registeredName;
        }
        
        // Split the name into parts for partial matching
        String[] nameParts = processedName.split("\\s+");
        int matchedParts = 0;
        StringBuilder matchedPartsDebug = new StringBuilder("Matched parts: ");
        
        for (String part : nameParts) {
            if (part.length() > 1 && processedText.contains(part)) { // Only consider parts longer than 1 character
                matchedParts++;
                matchedPartsDebug.append(part).append(", ");
            }
        }
        
        System.err.println(matchedPartsDebug.toString());
        
        // Consider it a match if we find enough parts of the name
        if (matchedParts >= 2 || (nameParts.length == 1 && matchedParts == 1)) {
            System.err.println("Found sufficient partial matches: " + matchedParts);
            return registeredName;
        }
        
        System.err.println("Name not found in text");
        return null;
    }

    public String verifyIDCard(String imagePath, String registeredName) {
        try {
            System.err.println("\n=== Starting ID verification ===");
            System.err.println("Image path: " + imagePath);
            System.err.println("Registered name: " + registeredName);
            
            File imageFile = new File(imagePath);
            if (!imageFile.exists()) {
                System.err.println("Error: Image file not found");
                return createErrorResponse("Image file not found: " + imagePath);
            }

            System.err.println("Extracting text from image...");
            String extractedText = tesseract.doOCR(imageFile);
            System.err.println("Raw extracted text:\n" + extractedText);
            
            // Extract enrollment number
            Matcher enrollmentMatcher = ENROLLMENT_PATTERN.matcher(extractedText);
            String enrollmentNumber = null;
            while (enrollmentMatcher.find()) {
                enrollmentNumber = enrollmentMatcher.group();
                System.err.println("Found enrollment number: " + enrollmentNumber);
            }
            
            // Look for registered name in the extracted text
            String foundName = findNameInText(extractedText, registeredName);
            
            if (foundName != null) {
                System.err.println("Successfully found name: " + foundName);
                return gson.toJson(new VerificationResult(true, 
                    "ID card verified successfully", enrollmentNumber, foundName));
            } else {
                System.err.println("Failed to find name: " + registeredName);
                return createErrorResponse("Could not find name '" + registeredName + "' on ID card. Please ensure the name matches exactly as shown on your ID.");
            }
            
        } catch (TesseractException e) {
            System.err.println("Tesseract error: " + e.getMessage());
            e.printStackTrace();
            return createErrorResponse("Error processing ID card: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("Unexpected error: " + e.getMessage());
            e.printStackTrace();
            return createErrorResponse("Unexpected error: " + e.getMessage());
        }
    }

    private String createErrorResponse(String message) {
        return gson.toJson(new VerificationResult(false, message, null, null));
    }

    public static void main(String[] args) {
        if (args.length < 2) {
            String errorJson = new GsonBuilder().setPrettyPrinting().create()
                .toJson(new VerificationResult(false, "Usage: java PythonIDVerifier <image_path> <registered_name>", null, null));
            System.out.println(errorJson);
            return;
        }

        try {
            PythonIDVerifier verifier = new PythonIDVerifier("tessdata");
            String result = verifier.verifyIDCard(args[0], args[1]);
            System.out.println(result);
        } catch (Exception e) {
            String errorJson = new GsonBuilder().setPrettyPrinting().create()
                .toJson(new VerificationResult(false, "Error: " + e.getMessage(), null, null));
            System.out.println(errorJson);
        }
    }
} 