import typing_extensions

from vartulz_compliance_sdk.paths import PathValues
from vartulz_compliance_sdk.apis.paths.v1_utility_signatory_details import V1UtilitySignatoryDetails
from vartulz_compliance_sdk.apis.paths.v1_utility_pan_verify import V1UtilityPanVerify
from vartulz_compliance_sdk.apis.paths.v1_utility_iec_details import V1UtilityIecDetails
from vartulz_compliance_sdk.apis.paths.v1_utility_electricity_details import V1UtilityElectricityDetails
from vartulz_compliance_sdk.apis.paths.v1_utility_company_master_details import V1UtilityCompanyMasterDetails
from vartulz_compliance_sdk.apis.paths.v1_utility_company_ciin_lookup import V1UtilityCompanyCiinLookup
from vartulz_compliance_sdk.apis.paths.v1_utility_bank_verify import V1UtilityBankVerify
from vartulz_compliance_sdk.apis.paths.v1_session_login import V1SessionLogin
from vartulz_compliance_sdk.apis.paths.v1_registration_forverify_pan_verify import V1RegistrationForverifyPanVerify
from vartulz_compliance_sdk.apis.paths.v1_registration_create_new import V1RegistrationCreateNew
from vartulz_compliance_sdk.apis.paths.v1_razor_create_payment_link import V1RazorCreatePaymentLink
from vartulz_compliance_sdk.apis.paths.v1_rate_new_create import V1RateNewCreate
from vartulz_compliance_sdk.apis.paths.v1_profile_update_password import V1ProfileUpdatePassword
from vartulz_compliance_sdk.apis.paths.v1_pan_get_details import V1PanGetDetails
from vartulz_compliance_sdk.apis.paths.v1_nsdl_update_signatory_details_case_id import V1NsdlUpdateSignatoryDetailsCaseId
from vartulz_compliance_sdk.apis.paths.v1_nsdl_update_master_details_case_id import V1NsdlUpdateMasterDetailsCaseId
from vartulz_compliance_sdk.apis.paths.v1_nsdl_update_iec_details_case_id import V1NsdlUpdateIecDetailsCaseId
from vartulz_compliance_sdk.apis.paths.v1_nsdl_update_electricitybill_details_case_id import V1NsdlUpdateElectricitybillDetailsCaseId
from vartulz_compliance_sdk.apis.paths.v1_gstin_update_track_details import V1GstinUpdateTrackDetails
from vartulz_compliance_sdk.apis.paths.v1_gstin_update_status import V1GstinUpdateStatus
from vartulz_compliance_sdk.apis.paths.v1_gstin_update_preference_details import V1GstinUpdatePreferenceDetails
from vartulz_compliance_sdk.apis.paths.v1_gstin_get_all_gstin import V1GstinGetAllGstin
from vartulz_compliance_sdk.apis.paths.v1_gstin_delete_gstin import V1GstinDeleteGstin
from vartulz_compliance_sdk.apis.paths.v1_gstin_add_gstin import V1GstinAddGstin
from vartulz_compliance_sdk.apis.paths.v1_excel_upload import V1ExcelUpload
from vartulz_compliance_sdk.apis.paths.v1_crypto_encrypt import V1CryptoEncrypt
from vartulz_compliance_sdk.apis.paths.v1_crypto_decrypt import V1CryptoDecrypt
from vartulz_compliance_sdk.apis.paths.v1_company_block_unblock import V1CompanyBlockUnblock
from vartulz_compliance_sdk.apis.paths.v1_case_create_new import V1CaseCreateNew
from vartulz_compliance_sdk.apis.paths.v1_barcode_share_barcode import V1BarcodeShareBarcode
from vartulz_compliance_sdk.apis.paths.v1_bank_delete_bank import V1BankDeleteBank
from vartulz_compliance_sdk.apis.paths.v1_bank_add_verify import V1BankAddVerify
from vartulz_compliance_sdk.apis.paths.v1_aadhar_submit_otp import V1AadharSubmitOtp
from vartulz_compliance_sdk.apis.paths.v1_aadhar_send_otp import V1AadharSendOtp
from vartulz_compliance_sdk.apis.paths.v1_utility_ret_type_getall import V1UtilityRetTypeGetall
from vartulz_compliance_sdk.apis.paths.v1_utility_gstin_get_track_details_gstin import V1UtilityGstinGetTrackDetailsGstin
from vartulz_compliance_sdk.apis.paths.v1_utility_gstin_get_status_gstin import V1UtilityGstinGetStatusGstin
from vartulz_compliance_sdk.apis.paths.v1_utility_gstin_get_preference_details_gstin import V1UtilityGstinGetPreferenceDetailsGstin
from vartulz_compliance_sdk.apis.paths.v1_utility_get_track_details_gstin import V1UtilityGetTrackDetailsGstin
from vartulz_compliance_sdk.apis.paths.v1_utility_get_status_gstin import V1UtilityGetStatusGstin
from vartulz_compliance_sdk.apis.paths.v1_utility_get_preference_details_gstin import V1UtilityGetPreferenceDetailsGstin
from vartulz_compliance_sdk.apis.paths.v1_utility_get_details_gstin import V1UtilityGetDetailsGstin
from vartulz_compliance_sdk.apis.paths.v1_utility_get_all_member import V1UtilityGetAllMember
from vartulz_compliance_sdk.apis.paths.v1_utility_get_all_details import V1UtilityGetAllDetails
from vartulz_compliance_sdk.apis.paths.v1_utility_fy_getall import V1UtilityFyGetall
from vartulz_compliance_sdk.apis.paths.v1_task_execute import V1TaskExecute
from vartulz_compliance_sdk.apis.paths.v1_session_logout import V1SessionLogout
from vartulz_compliance_sdk.apis.paths.v1_registration_forverify_get_details_gstin import V1RegistrationForverifyGetDetailsGstin
from vartulz_compliance_sdk.apis.paths.v1_razor_get_payment_details_payment_id import V1RazorGetPaymentDetailsPaymentId
from vartulz_compliance_sdk.apis.paths.v1_razor_get_all_payments_details import V1RazorGetAllPaymentsDetails
from vartulz_compliance_sdk.apis.paths.v1_rate_get_services import V1RateGetServices
from vartulz_compliance_sdk.apis.paths.v1_rate_get_all import V1RateGetAll
from vartulz_compliance_sdk.apis.paths.v1_profile_send_reset_link import V1ProfileSendResetLink
from vartulz_compliance_sdk.apis.paths.v1_profile_send_password_otp_company_id import V1ProfileSendPasswordOtpCompanyId
from vartulz_compliance_sdk.apis.paths.v1_profile_get_profile_company_id import V1ProfileGetProfileCompanyId
from vartulz_compliance_sdk.apis.paths.v1_profile_get_profile_balance import V1ProfileGetProfileBalance
from vartulz_compliance_sdk.apis.paths.v1_pan_get_details_bycase import V1PanGetDetailsBycase
from vartulz_compliance_sdk.apis.paths.v1_nsdl_get_signatory_details_case_id import V1NsdlGetSignatoryDetailsCaseId
from vartulz_compliance_sdk.apis.paths.v1_nsdl_get_master_details_case_id import V1NsdlGetMasterDetailsCaseId
from vartulz_compliance_sdk.apis.paths.v1_nsdl_get_iec_details_case_id import V1NsdlGetIecDetailsCaseId
from vartulz_compliance_sdk.apis.paths.v1_nsdl_get_electricitybill_details_case_id import V1NsdlGetElectricitybillDetailsCaseId
from vartulz_compliance_sdk.apis.paths.v1_excel_getall_uploadid import V1ExcelGetallUploadid
from vartulz_compliance_sdk.apis.paths.v1_excel_get_uploadid_records import V1ExcelGetUploadidRecords
from vartulz_compliance_sdk.apis.paths.v1_company_get_details_company_code import V1CompanyGetDetailsCompanyCode
from vartulz_compliance_sdk.apis.paths.v1_company_get_details_byfilter import V1CompanyGetDetailsByfilter
from vartulz_compliance_sdk.apis.paths.v1_company_get_all import V1CompanyGetAll
from vartulz_compliance_sdk.apis.paths.v1_company_get_all_forapproval import V1CompanyGetAllForapproval
from vartulz_compliance_sdk.apis.paths.v1_company_get_all_emailnotapproved import V1CompanyGetAllEmailnotapproved
from vartulz_compliance_sdk.apis.paths.v1_company_get_all_approved_rejected import V1CompanyGetAllApprovedRejected
from vartulz_compliance_sdk.apis.paths.v1_company_approve_reject import V1CompanyApproveReject
from vartulz_compliance_sdk.apis.paths.v1_case_get_all_case import V1CaseGetAllCase
from vartulz_compliance_sdk.apis.paths.v1_case_admin_get_all_case import V1CaseAdminGetAllCase
from vartulz_compliance_sdk.apis.paths.v1_biller_get_all_state import V1BillerGetAllState
from vartulz_compliance_sdk.apis.paths.v1_biller_get_all_bystate_state import V1BillerGetAllBystateState
from vartulz_compliance_sdk.apis.paths.v1_biller_get_all_biller import V1BillerGetAllBiller
from vartulz_compliance_sdk.apis.paths.v1_barcode_get_signatory_details import V1BarcodeGetSignatoryDetails
from vartulz_compliance_sdk.apis.paths.v1_barcode_get_pan_details import V1BarcodeGetPanDetails
from vartulz_compliance_sdk.apis.paths.v1_barcode_get_master_details import V1BarcodeGetMasterDetails
from vartulz_compliance_sdk.apis.paths.v1_barcode_get_iec_details import V1BarcodeGetIecDetails
from vartulz_compliance_sdk.apis.paths.v1_barcode_get_gstin_track_details_gstin import V1BarcodeGetGstinTrackDetailsGstin
from vartulz_compliance_sdk.apis.paths.v1_barcode_get_gstin_status_gstin import V1BarcodeGetGstinStatusGstin
from vartulz_compliance_sdk.apis.paths.v1_barcode_get_gstin_preference_details_gstin import V1BarcodeGetGstinPreferenceDetailsGstin
from vartulz_compliance_sdk.apis.paths.v1_barcode_get_gstin_details import V1BarcodeGetGstinDetails
from vartulz_compliance_sdk.apis.paths.v1_barcode_get_electricity_details import V1BarcodeGetElectricityDetails
from vartulz_compliance_sdk.apis.paths.v1_barcode_get_bank_details import V1BarcodeGetBankDetails
from vartulz_compliance_sdk.apis.paths.v1_barcode_get_aadhar_details import V1BarcodeGetAadharDetails
from vartulz_compliance_sdk.apis.paths.v1_barcode_generatre_barcode import V1BarcodeGeneratreBarcode
from vartulz_compliance_sdk.apis.paths.v1_bank_get_all import V1BankGetAll
from vartulz_compliance_sdk.apis.paths.v1_aadhar_get_all_aadhar import V1AadharGetAllAadhar
from vartulz_compliance_sdk.apis.paths.v1_aadhar_delete_aadhar import V1AadharDeleteAadhar

PathToApi = typing_extensions.TypedDict(
    'PathToApi',
    {
        PathValues.V1_UTILITY_SIGNATORY_DETAILS: V1UtilitySignatoryDetails,
        PathValues.V1_UTILITY_PAN_VERIFY: V1UtilityPanVerify,
        PathValues.V1_UTILITY_IEC_DETAILS: V1UtilityIecDetails,
        PathValues.V1_UTILITY_ELECTRICITY_DETAILS: V1UtilityElectricityDetails,
        PathValues.V1_UTILITY_COMPANY_MASTER_DETAILS: V1UtilityCompanyMasterDetails,
        PathValues.V1_UTILITY_COMPANY_CIIN_LOOKUP: V1UtilityCompanyCiinLookup,
        PathValues.V1_UTILITY_BANK_VERIFY: V1UtilityBankVerify,
        PathValues.V1_SESSION_LOGIN: V1SessionLogin,
        PathValues.V1_REGISTRATION_FORVERIFY_PAN_VERIFY: V1RegistrationForverifyPanVerify,
        PathValues.V1_REGISTRATION_CREATE_NEW: V1RegistrationCreateNew,
        PathValues.V1_RAZOR_CREATE_PAYMENT_LINK: V1RazorCreatePaymentLink,
        PathValues.V1_RATE_NEW_CREATE: V1RateNewCreate,
        PathValues.V1_PROFILE_UPDATE_PASSWORD: V1ProfileUpdatePassword,
        PathValues.V1_PAN_GET_DETAILS: V1PanGetDetails,
        PathValues.V1_NSDL_UPDATE_SIGNATORY_DETAILS_CASE_ID: V1NsdlUpdateSignatoryDetailsCaseId,
        PathValues.V1_NSDL_UPDATE_MASTER_DETAILS_CASE_ID: V1NsdlUpdateMasterDetailsCaseId,
        PathValues.V1_NSDL_UPDATE_IEC_DETAILS_CASE_ID: V1NsdlUpdateIecDetailsCaseId,
        PathValues.V1_NSDL_UPDATE_ELECTRICITYBILL_DETAILS_CASE_ID: V1NsdlUpdateElectricitybillDetailsCaseId,
        PathValues.V1_GSTIN_UPDATE_TRACK_DETAILS: V1GstinUpdateTrackDetails,
        PathValues.V1_GSTIN_UPDATE_STATUS: V1GstinUpdateStatus,
        PathValues.V1_GSTIN_UPDATE_PREFERENCE_DETAILS: V1GstinUpdatePreferenceDetails,
        PathValues.V1_GSTIN_GET_ALL_GSTIN: V1GstinGetAllGstin,
        PathValues.V1_GSTIN_DELETE_GSTIN: V1GstinDeleteGstin,
        PathValues.V1_GSTIN_ADD_GSTIN: V1GstinAddGstin,
        PathValues.V1_EXCEL_UPLOAD: V1ExcelUpload,
        PathValues.V1_CRYPTO_ENCRYPT: V1CryptoEncrypt,
        PathValues.V1_CRYPTO_DECRYPT: V1CryptoDecrypt,
        PathValues.V1_COMPANY_BLOCK_UNBLOCK: V1CompanyBlockUnblock,
        PathValues.V1_CASE_CREATE_NEW: V1CaseCreateNew,
        PathValues.V1_BARCODE_SHARE_BARCODE: V1BarcodeShareBarcode,
        PathValues.V1_BANK_DELETE_BANK: V1BankDeleteBank,
        PathValues.V1_BANK_ADD_VERIFY: V1BankAddVerify,
        PathValues.V1_AADHAR_SUBMIT_OTP: V1AadharSubmitOtp,
        PathValues.V1_AADHAR_SEND_OTP: V1AadharSendOtp,
        PathValues.V1_UTILITY_RET_TYPE_GETALL: V1UtilityRetTypeGetall,
        PathValues.V1_UTILITY_GSTIN_GET_TRACK_DETAILS_GSTIN: V1UtilityGstinGetTrackDetailsGstin,
        PathValues.V1_UTILITY_GSTIN_GET_STATUS_GSTIN: V1UtilityGstinGetStatusGstin,
        PathValues.V1_UTILITY_GSTIN_GET_PREFERENCE_DETAILS_GSTIN: V1UtilityGstinGetPreferenceDetailsGstin,
        PathValues.V1_UTILITY_GET_TRACK_DETAILS_GSTIN: V1UtilityGetTrackDetailsGstin,
        PathValues.V1_UTILITY_GET_STATUS_GSTIN: V1UtilityGetStatusGstin,
        PathValues.V1_UTILITY_GET_PREFERENCE_DETAILS_GSTIN: V1UtilityGetPreferenceDetailsGstin,
        PathValues.V1_UTILITY_GET_DETAILS_GSTIN: V1UtilityGetDetailsGstin,
        PathValues.V1_UTILITY_GET_ALL_MEMBER: V1UtilityGetAllMember,
        PathValues.V1_UTILITY_GET_ALL_DETAILS: V1UtilityGetAllDetails,
        PathValues.V1_UTILITY_FY_GETALL: V1UtilityFyGetall,
        PathValues.V1_TASK_EXECUTE: V1TaskExecute,
        PathValues.V1_SESSION_LOGOUT: V1SessionLogout,
        PathValues.V1_REGISTRATION_FORVERIFY_GET_DETAILS_GSTIN: V1RegistrationForverifyGetDetailsGstin,
        PathValues.V1_RAZOR_GET_PAYMENT_DETAILS_PAYMENT_ID: V1RazorGetPaymentDetailsPaymentId,
        PathValues.V1_RAZOR_GET_ALL_PAYMENTS_DETAILS: V1RazorGetAllPaymentsDetails,
        PathValues.V1_RATE_GET_SERVICES: V1RateGetServices,
        PathValues.V1_RATE_GET_ALL: V1RateGetAll,
        PathValues.V1_PROFILE_SEND_RESET_LINK: V1ProfileSendResetLink,
        PathValues.V1_PROFILE_SEND_PASSWORD_OTP_COMPANY_ID: V1ProfileSendPasswordOtpCompanyId,
        PathValues.V1_PROFILE_GET_PROFILE_COMPANY_ID: V1ProfileGetProfileCompanyId,
        PathValues.V1_PROFILE_GET_PROFILE_BALANCE: V1ProfileGetProfileBalance,
        PathValues.V1_PAN_GET_DETAILS_BYCASE: V1PanGetDetailsBycase,
        PathValues.V1_NSDL_GET_SIGNATORY_DETAILS_CASE_ID: V1NsdlGetSignatoryDetailsCaseId,
        PathValues.V1_NSDL_GET_MASTER_DETAILS_CASE_ID: V1NsdlGetMasterDetailsCaseId,
        PathValues.V1_NSDL_GET_IEC_DETAILS_CASE_ID: V1NsdlGetIecDetailsCaseId,
        PathValues.V1_NSDL_GET_ELECTRICITYBILL_DETAILS_CASE_ID: V1NsdlGetElectricitybillDetailsCaseId,
        PathValues.V1_EXCEL_GETALL_UPLOADID: V1ExcelGetallUploadid,
        PathValues.V1_EXCEL_GET_UPLOADID_RECORDS: V1ExcelGetUploadidRecords,
        PathValues.V1_COMPANY_GET_DETAILS_COMPANY_CODE: V1CompanyGetDetailsCompanyCode,
        PathValues.V1_COMPANY_GET_DETAILS_BYFILTER: V1CompanyGetDetailsByfilter,
        PathValues.V1_COMPANY_GET_ALL: V1CompanyGetAll,
        PathValues.V1_COMPANY_GET_ALL_FORAPPROVAL: V1CompanyGetAllForapproval,
        PathValues.V1_COMPANY_GET_ALL_EMAILNOTAPPROVED: V1CompanyGetAllEmailnotapproved,
        PathValues.V1_COMPANY_GET_ALL_APPROVED_REJECTED: V1CompanyGetAllApprovedRejected,
        PathValues.V1_COMPANY_APPROVE_REJECT: V1CompanyApproveReject,
        PathValues.V1_CASE_GET_ALL_CASE: V1CaseGetAllCase,
        PathValues.V1_CASE_ADMIN_GET_ALL_CASE: V1CaseAdminGetAllCase,
        PathValues.V1_BILLER_GET_ALL_STATE: V1BillerGetAllState,
        PathValues.V1_BILLER_GET_ALL_BYSTATE_STATE: V1BillerGetAllBystateState,
        PathValues.V1_BILLER_GET_ALL_BILLER: V1BillerGetAllBiller,
        PathValues.V1_BARCODE_GET_SIGNATORY_DETAILS: V1BarcodeGetSignatoryDetails,
        PathValues.V1_BARCODE_GET_PAN_DETAILS: V1BarcodeGetPanDetails,
        PathValues.V1_BARCODE_GET_MASTER_DETAILS: V1BarcodeGetMasterDetails,
        PathValues.V1_BARCODE_GET_IEC_DETAILS: V1BarcodeGetIecDetails,
        PathValues.V1_BARCODE_GET_GSTIN_TRACK_DETAILS_GSTIN: V1BarcodeGetGstinTrackDetailsGstin,
        PathValues.V1_BARCODE_GET_GSTIN_STATUS_GSTIN: V1BarcodeGetGstinStatusGstin,
        PathValues.V1_BARCODE_GET_GSTIN_PREFERENCE_DETAILS_GSTIN: V1BarcodeGetGstinPreferenceDetailsGstin,
        PathValues.V1_BARCODE_GET_GSTIN_DETAILS: V1BarcodeGetGstinDetails,
        PathValues.V1_BARCODE_GET_ELECTRICITY_DETAILS: V1BarcodeGetElectricityDetails,
        PathValues.V1_BARCODE_GET_BANK_DETAILS: V1BarcodeGetBankDetails,
        PathValues.V1_BARCODE_GET_AADHAR_DETAILS: V1BarcodeGetAadharDetails,
        PathValues.V1_BARCODE_GENERATRE_BARCODE: V1BarcodeGeneratreBarcode,
        PathValues.V1_BANK_GET_ALL: V1BankGetAll,
        PathValues.V1_AADHAR_GET_ALL_AADHAR: V1AadharGetAllAadhar,
        PathValues.V1_AADHAR_DELETE_AADHAR: V1AadharDeleteAadhar,
    }
)

path_to_api = PathToApi(
    {
        PathValues.V1_UTILITY_SIGNATORY_DETAILS: V1UtilitySignatoryDetails,
        PathValues.V1_UTILITY_PAN_VERIFY: V1UtilityPanVerify,
        PathValues.V1_UTILITY_IEC_DETAILS: V1UtilityIecDetails,
        PathValues.V1_UTILITY_ELECTRICITY_DETAILS: V1UtilityElectricityDetails,
        PathValues.V1_UTILITY_COMPANY_MASTER_DETAILS: V1UtilityCompanyMasterDetails,
        PathValues.V1_UTILITY_COMPANY_CIIN_LOOKUP: V1UtilityCompanyCiinLookup,
        PathValues.V1_UTILITY_BANK_VERIFY: V1UtilityBankVerify,
        PathValues.V1_SESSION_LOGIN: V1SessionLogin,
        PathValues.V1_REGISTRATION_FORVERIFY_PAN_VERIFY: V1RegistrationForverifyPanVerify,
        PathValues.V1_REGISTRATION_CREATE_NEW: V1RegistrationCreateNew,
        PathValues.V1_RAZOR_CREATE_PAYMENT_LINK: V1RazorCreatePaymentLink,
        PathValues.V1_RATE_NEW_CREATE: V1RateNewCreate,
        PathValues.V1_PROFILE_UPDATE_PASSWORD: V1ProfileUpdatePassword,
        PathValues.V1_PAN_GET_DETAILS: V1PanGetDetails,
        PathValues.V1_NSDL_UPDATE_SIGNATORY_DETAILS_CASE_ID: V1NsdlUpdateSignatoryDetailsCaseId,
        PathValues.V1_NSDL_UPDATE_MASTER_DETAILS_CASE_ID: V1NsdlUpdateMasterDetailsCaseId,
        PathValues.V1_NSDL_UPDATE_IEC_DETAILS_CASE_ID: V1NsdlUpdateIecDetailsCaseId,
        PathValues.V1_NSDL_UPDATE_ELECTRICITYBILL_DETAILS_CASE_ID: V1NsdlUpdateElectricitybillDetailsCaseId,
        PathValues.V1_GSTIN_UPDATE_TRACK_DETAILS: V1GstinUpdateTrackDetails,
        PathValues.V1_GSTIN_UPDATE_STATUS: V1GstinUpdateStatus,
        PathValues.V1_GSTIN_UPDATE_PREFERENCE_DETAILS: V1GstinUpdatePreferenceDetails,
        PathValues.V1_GSTIN_GET_ALL_GSTIN: V1GstinGetAllGstin,
        PathValues.V1_GSTIN_DELETE_GSTIN: V1GstinDeleteGstin,
        PathValues.V1_GSTIN_ADD_GSTIN: V1GstinAddGstin,
        PathValues.V1_EXCEL_UPLOAD: V1ExcelUpload,
        PathValues.V1_CRYPTO_ENCRYPT: V1CryptoEncrypt,
        PathValues.V1_CRYPTO_DECRYPT: V1CryptoDecrypt,
        PathValues.V1_COMPANY_BLOCK_UNBLOCK: V1CompanyBlockUnblock,
        PathValues.V1_CASE_CREATE_NEW: V1CaseCreateNew,
        PathValues.V1_BARCODE_SHARE_BARCODE: V1BarcodeShareBarcode,
        PathValues.V1_BANK_DELETE_BANK: V1BankDeleteBank,
        PathValues.V1_BANK_ADD_VERIFY: V1BankAddVerify,
        PathValues.V1_AADHAR_SUBMIT_OTP: V1AadharSubmitOtp,
        PathValues.V1_AADHAR_SEND_OTP: V1AadharSendOtp,
        PathValues.V1_UTILITY_RET_TYPE_GETALL: V1UtilityRetTypeGetall,
        PathValues.V1_UTILITY_GSTIN_GET_TRACK_DETAILS_GSTIN: V1UtilityGstinGetTrackDetailsGstin,
        PathValues.V1_UTILITY_GSTIN_GET_STATUS_GSTIN: V1UtilityGstinGetStatusGstin,
        PathValues.V1_UTILITY_GSTIN_GET_PREFERENCE_DETAILS_GSTIN: V1UtilityGstinGetPreferenceDetailsGstin,
        PathValues.V1_UTILITY_GET_TRACK_DETAILS_GSTIN: V1UtilityGetTrackDetailsGstin,
        PathValues.V1_UTILITY_GET_STATUS_GSTIN: V1UtilityGetStatusGstin,
        PathValues.V1_UTILITY_GET_PREFERENCE_DETAILS_GSTIN: V1UtilityGetPreferenceDetailsGstin,
        PathValues.V1_UTILITY_GET_DETAILS_GSTIN: V1UtilityGetDetailsGstin,
        PathValues.V1_UTILITY_GET_ALL_MEMBER: V1UtilityGetAllMember,
        PathValues.V1_UTILITY_GET_ALL_DETAILS: V1UtilityGetAllDetails,
        PathValues.V1_UTILITY_FY_GETALL: V1UtilityFyGetall,
        PathValues.V1_TASK_EXECUTE: V1TaskExecute,
        PathValues.V1_SESSION_LOGOUT: V1SessionLogout,
        PathValues.V1_REGISTRATION_FORVERIFY_GET_DETAILS_GSTIN: V1RegistrationForverifyGetDetailsGstin,
        PathValues.V1_RAZOR_GET_PAYMENT_DETAILS_PAYMENT_ID: V1RazorGetPaymentDetailsPaymentId,
        PathValues.V1_RAZOR_GET_ALL_PAYMENTS_DETAILS: V1RazorGetAllPaymentsDetails,
        PathValues.V1_RATE_GET_SERVICES: V1RateGetServices,
        PathValues.V1_RATE_GET_ALL: V1RateGetAll,
        PathValues.V1_PROFILE_SEND_RESET_LINK: V1ProfileSendResetLink,
        PathValues.V1_PROFILE_SEND_PASSWORD_OTP_COMPANY_ID: V1ProfileSendPasswordOtpCompanyId,
        PathValues.V1_PROFILE_GET_PROFILE_COMPANY_ID: V1ProfileGetProfileCompanyId,
        PathValues.V1_PROFILE_GET_PROFILE_BALANCE: V1ProfileGetProfileBalance,
        PathValues.V1_PAN_GET_DETAILS_BYCASE: V1PanGetDetailsBycase,
        PathValues.V1_NSDL_GET_SIGNATORY_DETAILS_CASE_ID: V1NsdlGetSignatoryDetailsCaseId,
        PathValues.V1_NSDL_GET_MASTER_DETAILS_CASE_ID: V1NsdlGetMasterDetailsCaseId,
        PathValues.V1_NSDL_GET_IEC_DETAILS_CASE_ID: V1NsdlGetIecDetailsCaseId,
        PathValues.V1_NSDL_GET_ELECTRICITYBILL_DETAILS_CASE_ID: V1NsdlGetElectricitybillDetailsCaseId,
        PathValues.V1_EXCEL_GETALL_UPLOADID: V1ExcelGetallUploadid,
        PathValues.V1_EXCEL_GET_UPLOADID_RECORDS: V1ExcelGetUploadidRecords,
        PathValues.V1_COMPANY_GET_DETAILS_COMPANY_CODE: V1CompanyGetDetailsCompanyCode,
        PathValues.V1_COMPANY_GET_DETAILS_BYFILTER: V1CompanyGetDetailsByfilter,
        PathValues.V1_COMPANY_GET_ALL: V1CompanyGetAll,
        PathValues.V1_COMPANY_GET_ALL_FORAPPROVAL: V1CompanyGetAllForapproval,
        PathValues.V1_COMPANY_GET_ALL_EMAILNOTAPPROVED: V1CompanyGetAllEmailnotapproved,
        PathValues.V1_COMPANY_GET_ALL_APPROVED_REJECTED: V1CompanyGetAllApprovedRejected,
        PathValues.V1_COMPANY_APPROVE_REJECT: V1CompanyApproveReject,
        PathValues.V1_CASE_GET_ALL_CASE: V1CaseGetAllCase,
        PathValues.V1_CASE_ADMIN_GET_ALL_CASE: V1CaseAdminGetAllCase,
        PathValues.V1_BILLER_GET_ALL_STATE: V1BillerGetAllState,
        PathValues.V1_BILLER_GET_ALL_BYSTATE_STATE: V1BillerGetAllBystateState,
        PathValues.V1_BILLER_GET_ALL_BILLER: V1BillerGetAllBiller,
        PathValues.V1_BARCODE_GET_SIGNATORY_DETAILS: V1BarcodeGetSignatoryDetails,
        PathValues.V1_BARCODE_GET_PAN_DETAILS: V1BarcodeGetPanDetails,
        PathValues.V1_BARCODE_GET_MASTER_DETAILS: V1BarcodeGetMasterDetails,
        PathValues.V1_BARCODE_GET_IEC_DETAILS: V1BarcodeGetIecDetails,
        PathValues.V1_BARCODE_GET_GSTIN_TRACK_DETAILS_GSTIN: V1BarcodeGetGstinTrackDetailsGstin,
        PathValues.V1_BARCODE_GET_GSTIN_STATUS_GSTIN: V1BarcodeGetGstinStatusGstin,
        PathValues.V1_BARCODE_GET_GSTIN_PREFERENCE_DETAILS_GSTIN: V1BarcodeGetGstinPreferenceDetailsGstin,
        PathValues.V1_BARCODE_GET_GSTIN_DETAILS: V1BarcodeGetGstinDetails,
        PathValues.V1_BARCODE_GET_ELECTRICITY_DETAILS: V1BarcodeGetElectricityDetails,
        PathValues.V1_BARCODE_GET_BANK_DETAILS: V1BarcodeGetBankDetails,
        PathValues.V1_BARCODE_GET_AADHAR_DETAILS: V1BarcodeGetAadharDetails,
        PathValues.V1_BARCODE_GENERATRE_BARCODE: V1BarcodeGeneratreBarcode,
        PathValues.V1_BANK_GET_ALL: V1BankGetAll,
        PathValues.V1_AADHAR_GET_ALL_AADHAR: V1AadharGetAllAadhar,
        PathValues.V1_AADHAR_DELETE_AADHAR: V1AadharDeleteAadhar,
    }
)
