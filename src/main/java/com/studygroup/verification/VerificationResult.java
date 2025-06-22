package com.studygroup.verification;

public class VerificationResult {
    private final boolean success;
    private final String message;
    private final String enrollmentNumber;
    private final String studentName;

    public VerificationResult(boolean success, String message, String enrollmentNumber, String studentName) {
        this.success = success;
        this.message = message;
        this.enrollmentNumber = enrollmentNumber;
        this.studentName = studentName;
    }

    public boolean isSuccess() {
        return success;
    }

    public String getMessage() {
        return message;
    }

    public String getEnrollmentNumber() {
        return enrollmentNumber;
    }

    public String getStudentName() {
        return studentName;
    }

    @Override
    public String toString() {
        return String.format("VerificationResult{success=%s, message='%s', enrollmentNumber='%s', studentName='%s'}", 
            success, message, enrollmentNumber, studentName);
    }
}