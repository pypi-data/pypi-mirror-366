# do not import all endpoints into this module because that uses a lot of memory and stack frames
# if you need the ability to import all endpoints from this module, import them with
# from vartulz_compliance_sdk.apis.tag_to_api import tag_to_api

import enum


class TagValues(str, enum.Enum):
    NSDL_ENC_DC_MANAGEMENT = "NSDL ENC DC Management"
    REGISTRATION_MANAGEMENT = "Registration Management"
    GSTIN_UTILITY_MANAGEMENT = "GSTIN Utility Management"
    TASK_MANAGEMENT = "Task Management"
    ELECTRICITY_BILL_DETAILS_MANAGEMENT = "Electricity Bill Details Management"
    COMPANY_MASTER_DETAILS_MANAGEMENT = "Company Master Details Management"
    CASE_MANAGEMENT = "Case Management"
    ELECTRICITY_BILLER_MANAGEMENT = "Electricity Biller Management"
    BANK_DETAILS_MANAGEMENT = "Bank Details Management"
    EXCEL_MANAGEMENT = "Excel Management"
    PROFILE_MANAGEMENT = "Profile Management"
    GSTIN_MANAGEMENT = "GSTIN Management"
    SESSION_MANAGEMENT = "Session Management"
    PAYMENT_DETAILS_MANAGEMENT = "Payment Details Management"
    IEC_DETAILS_MANAGEMENT = "IEC Details Management"
    MCA_SIGNATORY_DETAILS_MANAGEMENT = "MCA Signatory Details Management"
    BARCODE_MANAGEMENT = "Barcode Management"
    MEMEBER_OF_MANAGEMENT = "Memeber Of Management"
    PAN_MANAGEMENT = "PAN Management"
    UTILITY_MANAGEMENT = "Utility Management"
    ADMIN_COMPANY_MANAGEMENT = "Admin Company Management"
    RATE_MASTER_DETAILS_MANAGEMENT = "Rate Master Details Management"
    AADHAR_MANAGEMENT = "Aadhar Management"
