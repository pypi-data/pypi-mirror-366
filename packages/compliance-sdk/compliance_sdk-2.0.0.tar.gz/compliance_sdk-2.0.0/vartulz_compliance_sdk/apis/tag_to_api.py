import typing_extensions

from vartulz_compliance_sdk.apis.tags import TagValues
from vartulz_compliance_sdk.apis.tags.nsdlencdc_management_api import NSDLENCDCManagementApi
from vartulz_compliance_sdk.apis.tags.registration_management_api import RegistrationManagementApi
from vartulz_compliance_sdk.apis.tags.gstin_utility_management_api import GSTINUtilityManagementApi
from vartulz_compliance_sdk.apis.tags.task_management_api import TaskManagementApi
from vartulz_compliance_sdk.apis.tags.electricity_bill_details_management_api import ElectricityBillDetailsManagementApi
from vartulz_compliance_sdk.apis.tags.company_master_details_management_api import CompanyMasterDetailsManagementApi
from vartulz_compliance_sdk.apis.tags.case_management_api import CaseManagementApi
from vartulz_compliance_sdk.apis.tags.electricity_biller_management_api import ElectricityBillerManagementApi
from vartulz_compliance_sdk.apis.tags.bank_details_management_api import BankDetailsManagementApi
from vartulz_compliance_sdk.apis.tags.excel_management_api import ExcelManagementApi
from vartulz_compliance_sdk.apis.tags.profile_management_api import ProfileManagementApi
from vartulz_compliance_sdk.apis.tags.gstin_management_api import GSTINManagementApi
from vartulz_compliance_sdk.apis.tags.session_management_api import SessionManagementApi
from vartulz_compliance_sdk.apis.tags.payment_details_management_api import PaymentDetailsManagementApi
from vartulz_compliance_sdk.apis.tags.iec_details_management_api import IECDetailsManagementApi
from vartulz_compliance_sdk.apis.tags.mca_signatory_details_management_api import MCASignatoryDetailsManagementApi
from vartulz_compliance_sdk.apis.tags.barcode_management_api import BarcodeManagementApi
from vartulz_compliance_sdk.apis.tags.memeber_of_management_api import MemeberOfManagementApi
from vartulz_compliance_sdk.apis.tags.pan_management_api import PANManagementApi
from vartulz_compliance_sdk.apis.tags.utility_management_api import UtilityManagementApi
from vartulz_compliance_sdk.apis.tags.admin_company_management_api import AdminCompanyManagementApi
from vartulz_compliance_sdk.apis.tags.rate_master_details_management_api import RateMasterDetailsManagementApi
from vartulz_compliance_sdk.apis.tags.aadhar_management_api import AadharManagementApi

TagToApi = typing_extensions.TypedDict(
    'TagToApi',
    {
        TagValues.NSDL_ENC_DC_MANAGEMENT: NSDLENCDCManagementApi,
        TagValues.REGISTRATION_MANAGEMENT: RegistrationManagementApi,
        TagValues.GSTIN_UTILITY_MANAGEMENT: GSTINUtilityManagementApi,
        TagValues.TASK_MANAGEMENT: TaskManagementApi,
        TagValues.ELECTRICITY_BILL_DETAILS_MANAGEMENT: ElectricityBillDetailsManagementApi,
        TagValues.COMPANY_MASTER_DETAILS_MANAGEMENT: CompanyMasterDetailsManagementApi,
        TagValues.CASE_MANAGEMENT: CaseManagementApi,
        TagValues.ELECTRICITY_BILLER_MANAGEMENT: ElectricityBillerManagementApi,
        TagValues.BANK_DETAILS_MANAGEMENT: BankDetailsManagementApi,
        TagValues.EXCEL_MANAGEMENT: ExcelManagementApi,
        TagValues.PROFILE_MANAGEMENT: ProfileManagementApi,
        TagValues.GSTIN_MANAGEMENT: GSTINManagementApi,
        TagValues.SESSION_MANAGEMENT: SessionManagementApi,
        TagValues.PAYMENT_DETAILS_MANAGEMENT: PaymentDetailsManagementApi,
        TagValues.IEC_DETAILS_MANAGEMENT: IECDetailsManagementApi,
        TagValues.MCA_SIGNATORY_DETAILS_MANAGEMENT: MCASignatoryDetailsManagementApi,
        TagValues.BARCODE_MANAGEMENT: BarcodeManagementApi,
        TagValues.MEMEBER_OF_MANAGEMENT: MemeberOfManagementApi,
        TagValues.PAN_MANAGEMENT: PANManagementApi,
        TagValues.UTILITY_MANAGEMENT: UtilityManagementApi,
        TagValues.ADMIN_COMPANY_MANAGEMENT: AdminCompanyManagementApi,
        TagValues.RATE_MASTER_DETAILS_MANAGEMENT: RateMasterDetailsManagementApi,
        TagValues.AADHAR_MANAGEMENT: AadharManagementApi,
    }
)

tag_to_api = TagToApi(
    {
        TagValues.NSDL_ENC_DC_MANAGEMENT: NSDLENCDCManagementApi,
        TagValues.REGISTRATION_MANAGEMENT: RegistrationManagementApi,
        TagValues.GSTIN_UTILITY_MANAGEMENT: GSTINUtilityManagementApi,
        TagValues.TASK_MANAGEMENT: TaskManagementApi,
        TagValues.ELECTRICITY_BILL_DETAILS_MANAGEMENT: ElectricityBillDetailsManagementApi,
        TagValues.COMPANY_MASTER_DETAILS_MANAGEMENT: CompanyMasterDetailsManagementApi,
        TagValues.CASE_MANAGEMENT: CaseManagementApi,
        TagValues.ELECTRICITY_BILLER_MANAGEMENT: ElectricityBillerManagementApi,
        TagValues.BANK_DETAILS_MANAGEMENT: BankDetailsManagementApi,
        TagValues.EXCEL_MANAGEMENT: ExcelManagementApi,
        TagValues.PROFILE_MANAGEMENT: ProfileManagementApi,
        TagValues.GSTIN_MANAGEMENT: GSTINManagementApi,
        TagValues.SESSION_MANAGEMENT: SessionManagementApi,
        TagValues.PAYMENT_DETAILS_MANAGEMENT: PaymentDetailsManagementApi,
        TagValues.IEC_DETAILS_MANAGEMENT: IECDetailsManagementApi,
        TagValues.MCA_SIGNATORY_DETAILS_MANAGEMENT: MCASignatoryDetailsManagementApi,
        TagValues.BARCODE_MANAGEMENT: BarcodeManagementApi,
        TagValues.MEMEBER_OF_MANAGEMENT: MemeberOfManagementApi,
        TagValues.PAN_MANAGEMENT: PANManagementApi,
        TagValues.UTILITY_MANAGEMENT: UtilityManagementApi,
        TagValues.ADMIN_COMPANY_MANAGEMENT: AdminCompanyManagementApi,
        TagValues.RATE_MASTER_DETAILS_MANAGEMENT: RateMasterDetailsManagementApi,
        TagValues.AADHAR_MANAGEMENT: AadharManagementApi,
    }
)
