# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ...._utils import PropertyInfo

__all__ = [
    "ClaimSubmitParams",
    "ClaimInformation",
    "ClaimInformationClaimCodeInformation",
    "ClaimInformationClaimDateInformation",
    "ClaimInformationPrincipalDiagnosis",
    "ClaimInformationServiceLine",
    "ClaimInformationServiceLineInstitutionalService",
    "ClaimInformationServiceLineDrugIdentification",
    "ClaimInformationServiceLineLineAdjudicationInformation",
    "ClaimInformationServiceLineLineAdjudicationInformationLineAdjustment",
    "ClaimInformationServiceLineLineAdjudicationInformationLineAdjustmentClaimAdjustmentDetail",
    "ClaimInformationServiceLineLineAdjustmentInformation",
    "ClaimInformationServiceLineLineAdjustmentInformationClaimAdjustment",
    "ClaimInformationServiceLineLineAdjustmentInformationClaimAdjustmentClaimAdjustmentDetail",
    "ClaimInformationServiceLineLinePricingInformation",
    "ClaimInformationServiceLineLineRepricingInformation",
    "ClaimInformationServiceLineLineSupplementInformation",
    "ClaimInformationServiceLineLineSupplementInformationReportInformation",
    "ClaimInformationServiceLineOperatingPhysician",
    "ClaimInformationServiceLineOtherOperatingPhysician",
    "ClaimInformationServiceLineReferringProvider",
    "ClaimInformationServiceLineReferringProviderAddress",
    "ClaimInformationServiceLineReferringProviderContactInformation",
    "ClaimInformationServiceLineReferringProviderReferenceIdentification",
    "ClaimInformationServiceLineRenderingProvider",
    "ClaimInformationServiceLineRenderingProviderAddress",
    "ClaimInformationServiceLineRenderingProviderContactInformation",
    "ClaimInformationServiceLineRenderingProviderReferenceIdentification",
    "ClaimInformationServiceLineServiceLineDateInformation",
    "ClaimInformationServiceLineServiceLineReferenceInformation",
    "ClaimInformationServiceLineServiceLineReferenceInformationProviderControlNumber",
    "ClaimInformationServiceLineServiceLineReferenceInformationRepricedLineItemRefNumber",
    "ClaimInformationServiceLineServiceLineReferenceInformationAdjustedRepricedLineItemRefNumber",
    "ClaimInformationServiceLineServiceLineSupplementalInformation",
    "ClaimInformationAdmittingDiagnosis",
    "ClaimInformationClaimContractInformation",
    "ClaimInformationClaimNotes",
    "ClaimInformationClaimPricingInformation",
    "ClaimInformationClaimSupplementalInformation",
    "ClaimInformationClaimSupplementalInformationReportInformation",
    "ClaimInformationConditionCodesList",
    "ClaimInformationDiagnosisRelatedGroupInformation",
    "ClaimInformationEpsdtReferral",
    "ClaimInformationExternalCauseOfInjury",
    "ClaimInformationOccurrenceInformationList",
    "ClaimInformationOccurrenceSpanInformation",
    "ClaimInformationOtherDiagnosisInformationList",
    "ClaimInformationOtherProcedureInformationList",
    "ClaimInformationOtherSubscriberInformation",
    "ClaimInformationOtherSubscriberInformationOtherPayerName",
    "ClaimInformationOtherSubscriberInformationOtherPayerNameOtherPayerAddress",
    "ClaimInformationOtherSubscriberInformationOtherPayerNameOtherPayerSecondaryIdentifier",
    "ClaimInformationOtherSubscriberInformationOtherSubscriberName",
    "ClaimInformationOtherSubscriberInformationOtherSubscriberNameAddress",
    "ClaimInformationOtherSubscriberInformationClaimLevelAdjustment",
    "ClaimInformationOtherSubscriberInformationClaimLevelAdjustmentClaimAdjustmentDetail",
    "ClaimInformationOtherSubscriberInformationMedicareInpatientAdjudication",
    "ClaimInformationOtherSubscriberInformationMedicareOutpatientAdjudication",
    "ClaimInformationOtherSubscriberInformationOtherPayerAttendingProvider",
    "ClaimInformationOtherSubscriberInformationOtherPayerAttendingProviderOtherPayerAttendingProviderIdentifier",
    "ClaimInformationOtherSubscriberInformationOtherPayerBillingProvider",
    "ClaimInformationOtherSubscriberInformationOtherPayerBillingProviderOtherPayerBillingProviderIdentifier",
    "ClaimInformationOtherSubscriberInformationOtherPayerOperatingPhysician",
    "ClaimInformationOtherSubscriberInformationOtherPayerOperatingPhysicianOtherPayerOperatingPhysicianIdentifier",
    "ClaimInformationOtherSubscriberInformationOtherPayerOtherOperatingPhysician",
    "ClaimInformationOtherSubscriberInformationOtherPayerOtherOperatingPhysicianOtherPayerOtherOperatingPhysicianIdentifier",
    "ClaimInformationOtherSubscriberInformationOtherPayerReferringProvider",
    "ClaimInformationOtherSubscriberInformationOtherPayerReferringProviderOtherPayerReferringProviderIdentifier",
    "ClaimInformationOtherSubscriberInformationOtherPayerRenderingProvider",
    "ClaimInformationOtherSubscriberInformationOtherPayerRenderingProviderOtherPayerRenderingProviderIdentifier",
    "ClaimInformationOtherSubscriberInformationOtherPayerServiceFacilityLocation",
    "ClaimInformationOtherSubscriberInformationOtherPayerServiceFacilityLocationOtherPayerServiceFacilityLocationIdentifier",
    "ClaimInformationPatientReasonForVisit",
    "ClaimInformationPrincipalProcedureInformation",
    "ClaimInformationServiceFacilityLocation",
    "ClaimInformationServiceFacilityLocationAddress",
    "ClaimInformationValueInformationList",
    "Receiver",
    "Submitter",
    "SubmitterContactInformation",
    "Subscriber",
    "SubscriberAddress",
    "Attending",
    "AttendingAddress",
    "AttendingContactInformation",
    "Billing",
    "BillingAddress",
    "BillingContactInformation",
    "BillingPayToAddressName",
    "BillingPayToAddressNameAddress",
    "BillingPayToPlanName",
    "BillingPayToPlanNameAddress",
    "Dependent",
    "DependentAddress",
    "EventMapping",
    "OperatingPhysician",
    "OtherOperatingPhysician",
    "PayerAddress",
    "Provider",
    "ProviderAddress",
    "ProviderContactInformation",
    "Referring",
    "ReferringAddress",
    "ReferringContactInformation",
    "Rendering",
    "RenderingAddress",
    "RenderingContactInformation",
]


class ClaimSubmitParams(TypedDict, total=False):
    claim_information: Required[Annotated[ClaimInformation, PropertyInfo(alias="claimInformation")]]

    idempotency_key: Required[Annotated[str, PropertyInfo(alias="idempotencyKey")]]

    is_testing: Required[Annotated[bool, PropertyInfo(alias="isTesting")]]

    receiver: Required[Receiver]

    submitter: Required[Submitter]

    subscriber: Required[Subscriber]

    trading_partner_service_id: Required[Annotated[str, PropertyInfo(alias="tradingPartnerServiceId")]]

    attending: Attending

    billing: Billing

    billing_pay_to_address_name: Annotated[BillingPayToAddressName, PropertyInfo(alias="billingPayToAddressName")]

    billing_pay_to_plan_name: Annotated[BillingPayToPlanName, PropertyInfo(alias="billingPayToPlanName")]

    control_number: Annotated[str, PropertyInfo(alias="controlNumber")]

    correlation_id: Annotated[str, PropertyInfo(alias="correlationId")]

    dependent: Dependent

    event_mapping: Annotated[EventMapping, PropertyInfo(alias="eventMapping")]

    operating_physician: Annotated[OperatingPhysician, PropertyInfo(alias="operatingPhysician")]

    other_operating_physician: Annotated[OtherOperatingPhysician, PropertyInfo(alias="otherOperatingPhysician")]

    payer_address: Annotated[PayerAddress, PropertyInfo(alias="payerAddress")]

    providers: Iterable[Provider]

    referring: Referring

    rendering: Rendering

    trading_partner_name: Annotated[str, PropertyInfo(alias="tradingPartnerName")]


class ClaimInformationClaimCodeInformation(TypedDict, total=False):
    admission_type_code: Required[Annotated[str, PropertyInfo(alias="admissionTypeCode")]]

    patient_status_code: Required[Annotated[str, PropertyInfo(alias="patientStatusCode")]]

    admission_source_code: Annotated[str, PropertyInfo(alias="admissionSourceCode")]


class ClaimInformationClaimDateInformation(TypedDict, total=False):
    statement_begin_date: Required[Annotated[str, PropertyInfo(alias="statementBeginDate")]]

    statement_end_date: Required[Annotated[str, PropertyInfo(alias="statementEndDate")]]

    admission_date_and_hour: Annotated[str, PropertyInfo(alias="admissionDateAndHour")]

    discharge_hour: Annotated[str, PropertyInfo(alias="dischargeHour")]

    repricer_received_date: Annotated[str, PropertyInfo(alias="repricerReceivedDate")]


class ClaimInformationPrincipalDiagnosis(TypedDict, total=False):
    principal_diagnosis_code: Required[Annotated[str, PropertyInfo(alias="principalDiagnosisCode")]]

    qualifier_code: Required[Annotated[Literal["ABK", "BK"], PropertyInfo(alias="qualifierCode")]]

    present_on_admission_indicator: Annotated[
        Literal["N", "Y", "U", "W"], PropertyInfo(alias="presentOnAdmissionIndicator")
    ]


class ClaimInformationServiceLineInstitutionalService(TypedDict, total=False):
    line_item_charge_amount: Required[Annotated[str, PropertyInfo(alias="lineItemChargeAmount")]]

    measurement_unit: Required[Annotated[Literal["DA", "UN"], PropertyInfo(alias="measurementUnit")]]

    service_line_revenue_code: Required[Annotated[str, PropertyInfo(alias="serviceLineRevenueCode")]]

    service_unit_count: Required[Annotated[str, PropertyInfo(alias="serviceUnitCount")]]

    description: str

    non_covered_charge_amount: Annotated[str, PropertyInfo(alias="nonCoveredChargeAmount")]

    procedure_code: Annotated[str, PropertyInfo(alias="procedureCode")]

    procedure_identifier: Annotated[Literal["ER", "HC", "HP", "IV", "WK"], PropertyInfo(alias="procedureIdentifier")]

    procedure_modifiers: Annotated[List[str], PropertyInfo(alias="procedureModifiers")]


class ClaimInformationServiceLineDrugIdentification(TypedDict, total=False):
    measurement_unit_code: Required[
        Annotated[Literal["F2", "GR", "ME", "ML", "UN"], PropertyInfo(alias="measurementUnitCode")]
    ]

    national_drug_code: Required[Annotated[str, PropertyInfo(alias="nationalDrugCode")]]

    national_drug_unit_count: Required[Annotated[str, PropertyInfo(alias="nationalDrugUnitCount")]]

    link_sequence_number: Annotated[str, PropertyInfo(alias="linkSequenceNumber")]

    pharmacy_prescription_number: Annotated[str, PropertyInfo(alias="pharmacyPrescriptionNumber")]


class ClaimInformationServiceLineLineAdjudicationInformationLineAdjustmentClaimAdjustmentDetail(TypedDict, total=False):
    adjustment_amount: Required[Annotated[str, PropertyInfo(alias="adjustmentAmount")]]

    adjustment_reason_code: Required[Annotated[str, PropertyInfo(alias="adjustmentReasonCode")]]

    adjustment_quantity: Annotated[str, PropertyInfo(alias="adjustmentQuantity")]


class ClaimInformationServiceLineLineAdjudicationInformationLineAdjustment(TypedDict, total=False):
    adjustment_group_code: Required[
        Annotated[Literal["CO", "CR", "OA", "PI", "PR"], PropertyInfo(alias="adjustmentGroupCode")]
    ]

    claim_adjustment_details: Annotated[
        Iterable[ClaimInformationServiceLineLineAdjudicationInformationLineAdjustmentClaimAdjustmentDetail],
        PropertyInfo(alias="claimAdjustmentDetails"),
    ]


class ClaimInformationServiceLineLineAdjudicationInformation(TypedDict, total=False):
    adjudication_or_payment_date: Required[Annotated[str, PropertyInfo(alias="adjudicationOrPaymentDate")]]

    other_payer_primary_identifier: Required[Annotated[str, PropertyInfo(alias="otherPayerPrimaryIdentifier")]]

    paid_service_unit_count: Required[Annotated[str, PropertyInfo(alias="paidServiceUnitCount")]]

    service_line_paid_amount: Required[Annotated[str, PropertyInfo(alias="serviceLinePaidAmount")]]

    service_line_revenue_code: Required[Annotated[str, PropertyInfo(alias="serviceLineRevenueCode")]]

    bundled_line_number: Annotated[str, PropertyInfo(alias="bundledLineNumber")]

    line_adjustment: Annotated[
        Iterable[ClaimInformationServiceLineLineAdjudicationInformationLineAdjustment],
        PropertyInfo(alias="lineAdjustment"),
    ]

    procedure_code: Annotated[str, PropertyInfo(alias="procedureCode")]

    procedure_code_description: Annotated[str, PropertyInfo(alias="procedureCodeDescription")]

    procedure_modifier: Annotated[List[str], PropertyInfo(alias="procedureModifier")]

    product_or_service_id_qualifier: Annotated[
        Literal["ER", "HC", "HP", "IV", "WK"], PropertyInfo(alias="productOrServiceIDQualifier")
    ]

    remaining_patient_liability: Annotated[str, PropertyInfo(alias="remainingPatientLiability")]


class ClaimInformationServiceLineLineAdjustmentInformationClaimAdjustmentClaimAdjustmentDetail(TypedDict, total=False):
    adjustment_amount: Required[Annotated[str, PropertyInfo(alias="adjustmentAmount")]]

    adjustment_reason_code: Required[Annotated[str, PropertyInfo(alias="adjustmentReasonCode")]]

    adjustment_quantity: Annotated[str, PropertyInfo(alias="adjustmentQuantity")]


class ClaimInformationServiceLineLineAdjustmentInformationClaimAdjustment(TypedDict, total=False):
    adjustment_group_code: Required[
        Annotated[Literal["CO", "CR", "OA", "PI", "PR"], PropertyInfo(alias="adjustmentGroupCode")]
    ]

    claim_adjustment_details: Annotated[
        Iterable[ClaimInformationServiceLineLineAdjustmentInformationClaimAdjustmentClaimAdjustmentDetail],
        PropertyInfo(alias="claimAdjustmentDetails"),
    ]


class ClaimInformationServiceLineLineAdjustmentInformation(TypedDict, total=False):
    claim_paid_date: Required[Annotated[str, PropertyInfo(alias="claimPaidDate")]]

    other_payer_primary_identifier: Required[Annotated[str, PropertyInfo(alias="otherPayerPrimaryIdentifier")]]

    paid_service_unit_count: Required[Annotated[str, PropertyInfo(alias="paidServiceUnitCount")]]

    procedure_code: Required[Annotated[str, PropertyInfo(alias="procedureCode")]]

    remaining_patient_liability: Required[Annotated[str, PropertyInfo(alias="remainingPatientLiability")]]

    service_id_qualifier: Required[
        Annotated[Literal["ER", "HC", "HP", "IV", "WK"], PropertyInfo(alias="serviceIdQualifier")]
    ]

    service_line_paid_amount: Required[Annotated[str, PropertyInfo(alias="serviceLinePaidAmount")]]

    bundled_or_unbundled_line_number: Annotated[str, PropertyInfo(alias="bundledOrUnbundledLineNumber")]

    claim_adjustment: Annotated[
        ClaimInformationServiceLineLineAdjustmentInformationClaimAdjustment, PropertyInfo(alias="claimAdjustment")
    ]

    procedure_code_description: Annotated[str, PropertyInfo(alias="procedureCodeDescription")]

    procedure_modifiers: Annotated[List[str], PropertyInfo(alias="procedureModifiers")]


class ClaimInformationServiceLineLinePricingInformation(TypedDict, total=False):
    pricing_methodology_code: Required[
        Annotated[
            Literal["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14"],
            PropertyInfo(alias="pricingMethodologyCode"),
        ]
    ]

    repriced_allowed_amount: Required[Annotated[str, PropertyInfo(alias="repricedAllowedAmount")]]

    apg_amount: Annotated[str, PropertyInfo(alias="apgAmount")]

    apg_code: Annotated[str, PropertyInfo(alias="apgCode")]

    exception_code: Annotated[Literal["1", "2", "3", "4", "5", "6"], PropertyInfo(alias="exceptionCode")]

    flat_rate_amount: Annotated[str, PropertyInfo(alias="flatRateAmount")]

    measurement_unit_code: Annotated[Literal["DA", "UN"], PropertyInfo(alias="measurementUnitCode")]

    policy_compliance_code: Annotated[Literal["1", "2", "3", "4", "5"], PropertyInfo(alias="policyComplianceCode")]

    reject_reason_code: Annotated[Literal["T1", "T2", "T3", "T4", "T5", "T6"], PropertyInfo(alias="rejectReasonCode")]

    repriced_approved_hcpcs_code: Annotated[str, PropertyInfo(alias="repricedApprovedHCPCSCode")]

    repriced_approved_service_unit_count: Annotated[str, PropertyInfo(alias="repricedApprovedServiceUnitCount")]

    repriced_organization_identifier: Annotated[str, PropertyInfo(alias="repricedOrganizationIdentifier")]

    repriced_saving_amount: Annotated[str, PropertyInfo(alias="repricedSavingAmount")]

    service_id_qualifier: Annotated[Literal["ER", "HC", "HP", "IV", "WK"], PropertyInfo(alias="serviceIdQualifier")]


class ClaimInformationServiceLineLineRepricingInformation(TypedDict, total=False):
    pricing_methodology_code: Required[
        Annotated[
            Literal["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14"],
            PropertyInfo(alias="pricingMethodologyCode"),
        ]
    ]

    repriced_allowed_amount: Required[Annotated[str, PropertyInfo(alias="repricedAllowedAmount")]]

    exception_code: Annotated[Literal["1", "2", "3", "4", "5", "6"], PropertyInfo(alias="exceptionCode")]

    policy_compliance_code: Annotated[Literal["1", "2", "3", "4", "5"], PropertyInfo(alias="policyComplianceCode")]

    product_or_service_id_qualifier: Annotated[
        Literal["ER", "HC", "HP", "IV", "WK"], PropertyInfo(alias="productOrServiceIDQualifier")
    ]

    reject_reason_code: Annotated[Literal["T1", "T2", "T3", "T4", "T5", "T6"], PropertyInfo(alias="rejectReasonCode")]

    repriced_approved_amount: Annotated[str, PropertyInfo(alias="repricedApprovedAmount")]

    repriced_approved_drg_code: Annotated[str, PropertyInfo(alias="repricedApprovedDRGCode")]

    repriced_approved_hcpcs_code: Annotated[str, PropertyInfo(alias="repricedApprovedHCPCSCode")]

    repriced_approved_revenue_code: Annotated[str, PropertyInfo(alias="repricedApprovedRevenueCode")]

    repriced_approved_service_unit_code: Annotated[
        Literal["DA", "UN"], PropertyInfo(alias="repricedApprovedServiceUnitCode")
    ]

    repriced_approved_service_unit_count: Annotated[str, PropertyInfo(alias="repricedApprovedServiceUnitCount")]

    repriced_org_identifier: Annotated[str, PropertyInfo(alias="repricedOrgIdentifier")]

    repriced_per_diem: Annotated[str, PropertyInfo(alias="repricedPerDiem")]

    repriced_saving_amount: Annotated[str, PropertyInfo(alias="repricedSavingAmount")]


class ClaimInformationServiceLineLineSupplementInformationReportInformation(TypedDict, total=False):
    attachment_control_number: Required[Annotated[str, PropertyInfo(alias="attachmentControlNumber")]]

    attachment_report_type_code: Required[
        Annotated[
            Literal[
                "03",
                "04",
                "05",
                "06",
                "07",
                "08",
                "09",
                "10",
                "11",
                "13",
                "15",
                "21",
                "A3",
                "A4",
                "AM",
                "AS",
                "B2",
                "B3",
                "B4",
                "BR",
                "BS",
                "BT",
                "CB",
                "CK",
                "CT",
                "D2",
                "DA",
                "DB",
                "DG",
                "DJ",
                "DS",
                "EB",
                "HC",
                "HR",
                "I5",
                "IR",
                "LA",
                "M1",
                "MT",
                "NN",
                "OB",
                "OC",
                "OD",
                "OE",
                "OX",
                "OZ",
                "P4",
                "P5",
                "PE",
                "PN",
                "PO",
                "PQ",
                "PY",
                "PZ",
                "RB",
                "RR",
                "RT",
                "RX",
                "SG",
                "V5",
                "XP",
            ],
            PropertyInfo(alias="attachmentReportTypeCode"),
        ]
    ]

    attachment_transmission_code: Required[
        Annotated[Literal["AA", "BM", "EL", "EM", "FT", "FX"], PropertyInfo(alias="attachmentTransmissionCode")]
    ]


class ClaimInformationServiceLineLineSupplementInformation(TypedDict, total=False):
    adjusted_repriced_claim_ref_number: Annotated[str, PropertyInfo(alias="adjustedRepricedClaimRefNumber")]

    auto_accident_state: Annotated[str, PropertyInfo(alias="autoAccidentState")]

    claim_control_number: Annotated[str, PropertyInfo(alias="claimControlNumber")]

    claim_number: Annotated[str, PropertyInfo(alias="claimNumber")]

    demo_project_identifier: Annotated[str, PropertyInfo(alias="demoProjectIdentifier")]

    investigational_device_exemption_number: Annotated[str, PropertyInfo(alias="investigationalDeviceExemptionNumber")]

    medical_record_number: Annotated[str, PropertyInfo(alias="medicalRecordNumber")]

    peer_review_authorization_number: Annotated[str, PropertyInfo(alias="peerReviewAuthorizationNumber")]

    prior_authorization_number: Annotated[str, PropertyInfo(alias="priorAuthorizationNumber")]

    referral_number: Annotated[str, PropertyInfo(alias="referralNumber")]

    report_information: Annotated[
        ClaimInformationServiceLineLineSupplementInformationReportInformation, PropertyInfo(alias="reportInformation")
    ]

    report_informations: Annotated[
        Iterable[ClaimInformationServiceLineLineSupplementInformationReportInformation],
        PropertyInfo(alias="reportInformations"),
    ]

    repriced_claim_number: Annotated[str, PropertyInfo(alias="repricedClaimNumber")]

    service_authorization_exception_code: Annotated[
        Literal["1", "2", "3", "4", "5", "6", "7"], PropertyInfo(alias="serviceAuthorizationExceptionCode")
    ]


class ClaimInformationServiceLineOperatingPhysician(TypedDict, total=False):
    last_name: Required[Annotated[str, PropertyInfo(alias="lastName")]]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    identification_qualifier_code: Annotated[
        Literal["0B", "1G", "G2", "LU"], PropertyInfo(alias="identificationQualifierCode")
    ]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    secondary_identifier: Annotated[str, PropertyInfo(alias="secondaryIdentifier")]

    suffix: str


class ClaimInformationServiceLineOtherOperatingPhysician(TypedDict, total=False):
    last_name: Required[Annotated[str, PropertyInfo(alias="lastName")]]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    identification_qualifier_code: Annotated[
        Literal["0B", "1G", "G2", "LU"], PropertyInfo(alias="identificationQualifierCode")
    ]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    secondary_identifier: Annotated[str, PropertyInfo(alias="secondaryIdentifier")]

    suffix: str


class ClaimInformationServiceLineReferringProviderAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ClaimInformationServiceLineReferringProviderContactInformation(TypedDict, total=False):
    name: Required[str]

    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]

    valid_contact: Annotated[bool, PropertyInfo(alias="validContact")]


class ClaimInformationServiceLineReferringProviderReferenceIdentification(TypedDict, total=False):
    identifier: Required[str]

    qualifier: Required[str]


class ClaimInformationServiceLineReferringProvider(TypedDict, total=False):
    address: ClaimInformationServiceLineReferringProviderAddress

    commercial_number: Annotated[str, PropertyInfo(alias="commercialNumber")]

    contact_information: Annotated[
        ClaimInformationServiceLineReferringProviderContactInformation, PropertyInfo(alias="contactInformation")
    ]

    employer_id: Annotated[str, PropertyInfo(alias="employerId")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    location_number: Annotated[str, PropertyInfo(alias="locationNumber")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    provider_type: Annotated[Literal["ReferringProvider"], PropertyInfo(alias="providerType")]

    provider_upin_number: Annotated[str, PropertyInfo(alias="providerUpinNumber")]

    reference_identification: Annotated[
        Iterable[ClaimInformationServiceLineReferringProviderReferenceIdentification],
        PropertyInfo(alias="referenceIdentification"),
    ]

    secondary_identification_qualifier_code: Annotated[
        Literal["0B", "1G", "G2"], PropertyInfo(alias="secondaryIdentificationQualifierCode")
    ]

    secondary_identifier: Annotated[str, PropertyInfo(alias="secondaryIdentifier")]

    state_license_number: Annotated[str, PropertyInfo(alias="stateLicenseNumber")]

    suffix: str

    taxonomy_code: Annotated[str, PropertyInfo(alias="taxonomyCode")]


class ClaimInformationServiceLineRenderingProviderAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ClaimInformationServiceLineRenderingProviderContactInformation(TypedDict, total=False):
    name: Required[str]

    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]

    valid_contact: Annotated[bool, PropertyInfo(alias="validContact")]


class ClaimInformationServiceLineRenderingProviderReferenceIdentification(TypedDict, total=False):
    identifier: Required[str]

    qualifier: Required[str]


class ClaimInformationServiceLineRenderingProvider(TypedDict, total=False):
    address: ClaimInformationServiceLineRenderingProviderAddress

    commercial_number: Annotated[str, PropertyInfo(alias="commercialNumber")]

    contact_information: Annotated[
        ClaimInformationServiceLineRenderingProviderContactInformation, PropertyInfo(alias="contactInformation")
    ]

    employer_id: Annotated[str, PropertyInfo(alias="employerId")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    location_number: Annotated[str, PropertyInfo(alias="locationNumber")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    provider_type: Annotated[Literal["RenderingProvider"], PropertyInfo(alias="providerType")]

    provider_upin_number: Annotated[str, PropertyInfo(alias="providerUpinNumber")]

    reference_identification: Annotated[
        Iterable[ClaimInformationServiceLineRenderingProviderReferenceIdentification],
        PropertyInfo(alias="referenceIdentification"),
    ]

    secondary_identification_qualifier_code: Annotated[
        Literal["0B", "1G", "G2", "LU"], PropertyInfo(alias="secondaryIdentificationQualifierCode")
    ]

    secondary_identifier: Annotated[str, PropertyInfo(alias="secondaryIdentifier")]

    state_license_number: Annotated[str, PropertyInfo(alias="stateLicenseNumber")]

    suffix: str

    taxonomy_code: Annotated[str, PropertyInfo(alias="taxonomyCode")]


class ClaimInformationServiceLineServiceLineDateInformation(TypedDict, total=False):
    begin_service_date: Annotated[str, PropertyInfo(alias="beginServiceDate")]

    end_service_date: Annotated[str, PropertyInfo(alias="endServiceDate")]

    service_date: Annotated[str, PropertyInfo(alias="serviceDate")]

    valid_date_information: Annotated[bool, PropertyInfo(alias="validDateInformation")]


class ClaimInformationServiceLineServiceLineReferenceInformationProviderControlNumber(TypedDict, total=False):
    provider_control_number: Required[Annotated[str, PropertyInfo(alias="providerControlNumber")]]


class ClaimInformationServiceLineServiceLineReferenceInformationRepricedLineItemRefNumber(TypedDict, total=False):
    repriced_line_item_ref_number: Required[Annotated[str, PropertyInfo(alias="repricedLineItemRefNumber")]]


class ClaimInformationServiceLineServiceLineReferenceInformationAdjustedRepricedLineItemRefNumber(
    TypedDict, total=False
):
    adjusted_repriced_line_item_ref_number: Required[
        Annotated[str, PropertyInfo(alias="adjustedRepricedLineItemRefNumber")]
    ]


ClaimInformationServiceLineServiceLineReferenceInformation: TypeAlias = Union[
    ClaimInformationServiceLineServiceLineReferenceInformationProviderControlNumber,
    ClaimInformationServiceLineServiceLineReferenceInformationRepricedLineItemRefNumber,
    ClaimInformationServiceLineServiceLineReferenceInformationAdjustedRepricedLineItemRefNumber,
]


class ClaimInformationServiceLineServiceLineSupplementalInformation(TypedDict, total=False):
    attachment_report_type_code: Required[
        Annotated[
            Literal[
                "03",
                "04",
                "05",
                "06",
                "07",
                "08",
                "09",
                "10",
                "11",
                "13",
                "15",
                "21",
                "A3",
                "A4",
                "AM",
                "AS",
                "B2",
                "B3",
                "B4",
                "BR",
                "BS",
                "BT",
                "CB",
                "CK",
                "CT",
                "D2",
                "DA",
                "DB",
                "DG",
                "DJ",
                "DS",
                "EB",
                "HC",
                "HR",
                "I5",
                "IR",
                "LA",
                "M1",
                "MT",
                "NN",
                "OB",
                "OC",
                "OD",
                "OE",
                "OX",
                "OZ",
                "P4",
                "P5",
                "PE",
                "PN",
                "PO",
                "PQ",
                "PY",
                "PZ",
                "RB",
                "RR",
                "RT",
                "RX",
                "SG",
                "V5",
                "XP",
            ],
            PropertyInfo(alias="attachmentReportTypeCode"),
        ]
    ]

    attachment_transmission_code: Required[
        Annotated[Literal["AA", "BM", "EL", "EM", "FT", "FX"], PropertyInfo(alias="attachmentTransmissionCode")]
    ]

    attachment_control_number: Annotated[str, PropertyInfo(alias="attachmentControlNumber")]


class ClaimInformationServiceLine(TypedDict, total=False):
    institutional_service: Required[
        Annotated[ClaimInformationServiceLineInstitutionalService, PropertyInfo(alias="institutionalService")]
    ]

    adjusted_repriced_line_item_reference_number: Annotated[
        str, PropertyInfo(alias="adjustedRepricedLineItemReferenceNumber")
    ]

    assigned_number: Annotated[str, PropertyInfo(alias="assignedNumber")]

    description: str

    drug_identification: Annotated[
        ClaimInformationServiceLineDrugIdentification, PropertyInfo(alias="drugIdentification")
    ]

    facility_tax_amount: Annotated[str, PropertyInfo(alias="facilityTaxAmount")]

    line_adjudication_information: Annotated[
        Iterable[ClaimInformationServiceLineLineAdjudicationInformation],
        PropertyInfo(alias="lineAdjudicationInformation"),
    ]

    line_adjustment_information: Annotated[
        ClaimInformationServiceLineLineAdjustmentInformation, PropertyInfo(alias="lineAdjustmentInformation")
    ]

    line_note_text: Annotated[str, PropertyInfo(alias="lineNoteText")]

    line_pricing_information: Annotated[
        ClaimInformationServiceLineLinePricingInformation, PropertyInfo(alias="linePricingInformation")
    ]

    line_repricing_information: Annotated[
        ClaimInformationServiceLineLineRepricingInformation, PropertyInfo(alias="lineRepricingInformation")
    ]

    line_supplement_information: Annotated[
        ClaimInformationServiceLineLineSupplementInformation, PropertyInfo(alias="lineSupplementInformation")
    ]

    operating_physician: Annotated[
        ClaimInformationServiceLineOperatingPhysician, PropertyInfo(alias="operatingPhysician")
    ]

    other_operating_physician: Annotated[
        ClaimInformationServiceLineOtherOperatingPhysician, PropertyInfo(alias="otherOperatingPhysician")
    ]

    referring_provider: Annotated[ClaimInformationServiceLineReferringProvider, PropertyInfo(alias="referringProvider")]

    rendering_provider: Annotated[ClaimInformationServiceLineRenderingProvider, PropertyInfo(alias="renderingProvider")]

    repriced_line_item_reference_number: Annotated[str, PropertyInfo(alias="repricedLineItemReferenceNumber")]

    service_date: Annotated[str, PropertyInfo(alias="serviceDate")]

    service_date_end: Annotated[str, PropertyInfo(alias="serviceDateEnd")]

    service_line_date_information: Annotated[
        ClaimInformationServiceLineServiceLineDateInformation, PropertyInfo(alias="serviceLineDateInformation")
    ]

    service_line_reference_information: Annotated[
        ClaimInformationServiceLineServiceLineReferenceInformation,
        PropertyInfo(alias="serviceLineReferenceInformation"),
    ]

    service_line_supplemental_information: Annotated[
        ClaimInformationServiceLineServiceLineSupplementalInformation,
        PropertyInfo(alias="serviceLineSupplementalInformation"),
    ]

    service_line_supplemental_informations: Annotated[
        Iterable[ClaimInformationServiceLineServiceLineSupplementalInformation],
        PropertyInfo(alias="serviceLineSupplementalInformations"),
    ]

    service_tax_amount: Annotated[str, PropertyInfo(alias="serviceTaxAmount")]

    third_party_organization_notes: Annotated[str, PropertyInfo(alias="thirdPartyOrganizationNotes")]


class ClaimInformationAdmittingDiagnosis(TypedDict, total=False):
    admitting_diagnosis_code: Required[Annotated[str, PropertyInfo(alias="admittingDiagnosisCode")]]

    qualifier_code: Required[Annotated[Literal["ABJ", "BJ"], PropertyInfo(alias="qualifierCode")]]


class ClaimInformationClaimContractInformation(TypedDict, total=False):
    contract_type_code: Required[
        Annotated[Literal["01", "02", "03", "04", "05", "06", "09"], PropertyInfo(alias="contractTypeCode")]
    ]

    contract_amount: Annotated[str, PropertyInfo(alias="contractAmount")]

    contract_code: Annotated[str, PropertyInfo(alias="contractCode")]

    contract_percentage: Annotated[str, PropertyInfo(alias="contractPercentage")]

    contract_version_identifier: Annotated[str, PropertyInfo(alias="contractVersionIdentifier")]

    terms_discount_percentage: Annotated[str, PropertyInfo(alias="termsDiscountPercentage")]


class ClaimInformationClaimNotes(TypedDict, total=False):
    additional_information: Annotated[List[str], PropertyInfo(alias="additionalInformation")]

    allergies: List[str]

    diagnosis_description: Annotated[List[str], PropertyInfo(alias="diagnosisDescription")]

    dme: List[str]

    functional_limits_or_reason_homebound: Annotated[List[str], PropertyInfo(alias="functionalLimitsOrReasonHomebound")]

    goal_rehab_or_discharge_plans: Annotated[List[str], PropertyInfo(alias="goalRehabOrDischargePlans")]

    medications: List[str]

    nutritional_requirments: Annotated[List[str], PropertyInfo(alias="nutritionalRequirments")]

    orders_for_discip_lines_and_treatments: Annotated[
        List[str], PropertyInfo(alias="ordersForDiscipLinesAndTreatments")
    ]

    reasons_patient_leaves_home: Annotated[List[str], PropertyInfo(alias="reasonsPatientLeavesHome")]

    safety_measures: Annotated[List[str], PropertyInfo(alias="safetyMeasures")]

    supplemental_plan_of_treatment: Annotated[List[str], PropertyInfo(alias="supplementalPlanOfTreatment")]

    times_and_reasons_patient_not_at_home: Annotated[List[str], PropertyInfo(alias="timesAndReasonsPatientNotAtHome")]

    unusual_home_or_social_env: Annotated[List[str], PropertyInfo(alias="unusualHomeOrSocialEnv")]

    updated_information: Annotated[List[str], PropertyInfo(alias="updatedInformation")]


class ClaimInformationClaimPricingInformation(TypedDict, total=False):
    pricing_methodology_code: Required[
        Annotated[
            Literal["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14"],
            PropertyInfo(alias="pricingMethodologyCode"),
        ]
    ]

    repriced_allowed_amount: Required[Annotated[str, PropertyInfo(alias="repricedAllowedAmount")]]

    exception_code: Annotated[Literal["1", "2", "3", "4", "5", "6"], PropertyInfo(alias="exceptionCode")]

    policy_compliance_code: Annotated[Literal["1", "2", "3", "4", "5"], PropertyInfo(alias="policyComplianceCode")]

    product_or_service_id_qualifier: Annotated[
        Literal["ER", "HC", "HP", "IV", "WK"], PropertyInfo(alias="productOrServiceIDQualifier")
    ]

    reject_reason_code: Annotated[Literal["T1", "T2", "T3", "T4", "T5", "T6"], PropertyInfo(alias="rejectReasonCode")]

    repriced_approved_amount: Annotated[str, PropertyInfo(alias="repricedApprovedAmount")]

    repriced_approved_drg_code: Annotated[str, PropertyInfo(alias="repricedApprovedDRGCode")]

    repriced_approved_hcpcs_code: Annotated[str, PropertyInfo(alias="repricedApprovedHCPCSCode")]

    repriced_approved_revenue_code: Annotated[str, PropertyInfo(alias="repricedApprovedRevenueCode")]

    repriced_approved_service_unit_code: Annotated[
        Literal["DA", "UN"], PropertyInfo(alias="repricedApprovedServiceUnitCode")
    ]

    repriced_approved_service_unit_count: Annotated[str, PropertyInfo(alias="repricedApprovedServiceUnitCount")]

    repriced_org_identifier: Annotated[str, PropertyInfo(alias="repricedOrgIdentifier")]

    repriced_per_diem: Annotated[str, PropertyInfo(alias="repricedPerDiem")]

    repriced_saving_amount: Annotated[str, PropertyInfo(alias="repricedSavingAmount")]


class ClaimInformationClaimSupplementalInformationReportInformation(TypedDict, total=False):
    attachment_control_number: Required[Annotated[str, PropertyInfo(alias="attachmentControlNumber")]]

    attachment_report_type_code: Required[
        Annotated[
            Literal[
                "03",
                "04",
                "05",
                "06",
                "07",
                "08",
                "09",
                "10",
                "11",
                "13",
                "15",
                "21",
                "A3",
                "A4",
                "AM",
                "AS",
                "B2",
                "B3",
                "B4",
                "BR",
                "BS",
                "BT",
                "CB",
                "CK",
                "CT",
                "D2",
                "DA",
                "DB",
                "DG",
                "DJ",
                "DS",
                "EB",
                "HC",
                "HR",
                "I5",
                "IR",
                "LA",
                "M1",
                "MT",
                "NN",
                "OB",
                "OC",
                "OD",
                "OE",
                "OX",
                "OZ",
                "P4",
                "P5",
                "PE",
                "PN",
                "PO",
                "PQ",
                "PY",
                "PZ",
                "RB",
                "RR",
                "RT",
                "RX",
                "SG",
                "V5",
                "XP",
            ],
            PropertyInfo(alias="attachmentReportTypeCode"),
        ]
    ]

    attachment_transmission_code: Required[
        Annotated[Literal["AA", "BM", "EL", "EM", "FT", "FX"], PropertyInfo(alias="attachmentTransmissionCode")]
    ]


class ClaimInformationClaimSupplementalInformation(TypedDict, total=False):
    adjusted_repriced_claim_ref_number: Annotated[str, PropertyInfo(alias="adjustedRepricedClaimRefNumber")]

    auto_accident_state: Annotated[str, PropertyInfo(alias="autoAccidentState")]

    claim_control_number: Annotated[str, PropertyInfo(alias="claimControlNumber")]

    claim_number: Annotated[str, PropertyInfo(alias="claimNumber")]

    demo_project_identifier: Annotated[str, PropertyInfo(alias="demoProjectIdentifier")]

    investigational_device_exemption_number: Annotated[str, PropertyInfo(alias="investigationalDeviceExemptionNumber")]

    medical_record_number: Annotated[str, PropertyInfo(alias="medicalRecordNumber")]

    peer_review_authorization_number: Annotated[str, PropertyInfo(alias="peerReviewAuthorizationNumber")]

    prior_authorization_number: Annotated[str, PropertyInfo(alias="priorAuthorizationNumber")]

    referral_number: Annotated[str, PropertyInfo(alias="referralNumber")]

    report_information: Annotated[
        ClaimInformationClaimSupplementalInformationReportInformation, PropertyInfo(alias="reportInformation")
    ]

    report_informations: Annotated[
        Iterable[ClaimInformationClaimSupplementalInformationReportInformation],
        PropertyInfo(alias="reportInformations"),
    ]

    repriced_claim_number: Annotated[str, PropertyInfo(alias="repricedClaimNumber")]

    service_authorization_exception_code: Annotated[
        Literal["1", "2", "3", "4", "5", "6", "7"], PropertyInfo(alias="serviceAuthorizationExceptionCode")
    ]


class ClaimInformationConditionCodesList(TypedDict, total=False):
    condition_code: Required[Annotated[str, PropertyInfo(alias="conditionCode")]]


class ClaimInformationDiagnosisRelatedGroupInformation(TypedDict, total=False):
    drug_related_group_code: Required[Annotated[str, PropertyInfo(alias="drugRelatedGroupCode")]]


class ClaimInformationEpsdtReferral(TypedDict, total=False):
    certification_condition_code_applies_indicator: Required[
        Annotated[Literal["N", "Y"], PropertyInfo(alias="certificationConditionCodeAppliesIndicator")]
    ]

    condition_codes: Required[Annotated[List[Literal["AV", "NU", "S2", "ST"]], PropertyInfo(alias="conditionCodes")]]


class ClaimInformationExternalCauseOfInjury(TypedDict, total=False):
    external_cause_of_injury: Required[Annotated[str, PropertyInfo(alias="externalCauseOfInjury")]]

    qualifier_code: Required[Annotated[Literal["ABN", "BN"], PropertyInfo(alias="qualifierCode")]]

    present_on_admission_indicator: Annotated[
        Literal["N", "U", "Y", "W"], PropertyInfo(alias="presentOnAdmissionIndicator")
    ]


class ClaimInformationOccurrenceInformationList(TypedDict, total=False):
    occurrence_span_code: Required[Annotated[str, PropertyInfo(alias="occurrenceSpanCode")]]

    occurrence_span_code_date: Required[Annotated[str, PropertyInfo(alias="occurrenceSpanCodeDate")]]


class ClaimInformationOccurrenceSpanInformation(TypedDict, total=False):
    occurrence_span_code: Required[Annotated[str, PropertyInfo(alias="occurrenceSpanCode")]]

    occurrence_span_code_end_date: Required[Annotated[str, PropertyInfo(alias="occurrenceSpanCodeEndDate")]]

    occurrence_span_code_start_date: Required[Annotated[str, PropertyInfo(alias="occurrenceSpanCodeStartDate")]]


class ClaimInformationOtherDiagnosisInformationList(TypedDict, total=False):
    other_diagnosis_code: Required[Annotated[str, PropertyInfo(alias="otherDiagnosisCode")]]

    qualifier_code: Required[Annotated[Literal["ABF", "BF"], PropertyInfo(alias="qualifierCode")]]

    present_on_admission_indicator: Annotated[
        Literal["N", "Y", "U", "W"], PropertyInfo(alias="presentOnAdmissionIndicator")
    ]


class ClaimInformationOtherProcedureInformationList(TypedDict, total=False):
    other_procedure_code: Required[Annotated[str, PropertyInfo(alias="otherProcedureCode")]]

    qualifier_code: Required[Annotated[Literal["BBQ", "BQ"], PropertyInfo(alias="qualifierCode")]]

    other_procedure_date: Annotated[str, PropertyInfo(alias="otherProcedureDate")]


class ClaimInformationOtherSubscriberInformationOtherPayerNameOtherPayerAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ClaimInformationOtherSubscriberInformationOtherPayerNameOtherPayerSecondaryIdentifier(TypedDict, total=False):
    identifier: Required[str]

    qualifier: Required[str]


class ClaimInformationOtherSubscriberInformationOtherPayerName(TypedDict, total=False):
    other_payer_identifier: Required[Annotated[str, PropertyInfo(alias="otherPayerIdentifier")]]

    other_payer_identifier_type_code: Required[
        Annotated[Literal["PI", "XV"], PropertyInfo(alias="otherPayerIdentifierTypeCode")]
    ]

    other_payer_organization_name: Required[Annotated[str, PropertyInfo(alias="otherPayerOrganizationName")]]

    other_insured_additional_identifier: Annotated[str, PropertyInfo(alias="otherInsuredAdditionalIdentifier")]

    other_payer_address: Annotated[
        ClaimInformationOtherSubscriberInformationOtherPayerNameOtherPayerAddress,
        PropertyInfo(alias="otherPayerAddress"),
    ]

    other_payer_adjudication_or_payment_date: Annotated[str, PropertyInfo(alias="otherPayerAdjudicationOrPaymentDate")]

    other_payer_claim_adjustment_indicator: Annotated[bool, PropertyInfo(alias="otherPayerClaimAdjustmentIndicator")]

    other_payer_claim_control_number: Annotated[str, PropertyInfo(alias="otherPayerClaimControlNumber")]

    other_payer_prior_authorization_number: Annotated[str, PropertyInfo(alias="otherPayerPriorAuthorizationNumber")]

    other_payer_prior_authorization_or_referral_number: Annotated[
        str, PropertyInfo(alias="otherPayerPriorAuthorizationOrReferralNumber")
    ]

    other_payer_secondary_identifier: Annotated[
        Iterable[ClaimInformationOtherSubscriberInformationOtherPayerNameOtherPayerSecondaryIdentifier],
        PropertyInfo(alias="otherPayerSecondaryIdentifier"),
    ]


class ClaimInformationOtherSubscriberInformationOtherSubscriberNameAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ClaimInformationOtherSubscriberInformationOtherSubscriberName(TypedDict, total=False):
    other_insured_identifier: Required[Annotated[str, PropertyInfo(alias="otherInsuredIdentifier")]]

    other_insured_identifier_type_code: Required[
        Annotated[Literal["II", "MI"], PropertyInfo(alias="otherInsuredIdentifierTypeCode")]
    ]

    other_insured_last_name: Required[Annotated[str, PropertyInfo(alias="otherInsuredLastName")]]

    other_insured_qualifier: Required[Annotated[Literal["1", "2"], PropertyInfo(alias="otherInsuredQualifier")]]

    address: ClaimInformationOtherSubscriberInformationOtherSubscriberNameAddress

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    other_insured_additional_identifier: Annotated[List[str], PropertyInfo(alias="otherInsuredAdditionalIdentifier")]

    other_insured_first_name: Annotated[str, PropertyInfo(alias="otherInsuredFirstName")]

    other_insured_middle_name: Annotated[str, PropertyInfo(alias="otherInsuredMiddleName")]

    other_insured_suffix: Annotated[str, PropertyInfo(alias="otherInsuredSuffix")]


class ClaimInformationOtherSubscriberInformationClaimLevelAdjustmentClaimAdjustmentDetail(TypedDict, total=False):
    adjustment_amount: Required[Annotated[str, PropertyInfo(alias="adjustmentAmount")]]

    adjustment_reason_code: Required[Annotated[str, PropertyInfo(alias="adjustmentReasonCode")]]

    adjustment_quantity: Annotated[str, PropertyInfo(alias="adjustmentQuantity")]


class ClaimInformationOtherSubscriberInformationClaimLevelAdjustment(TypedDict, total=False):
    adjustment_group_code: Required[
        Annotated[Literal["CO", "CR", "OA", "PI", "PR"], PropertyInfo(alias="adjustmentGroupCode")]
    ]

    claim_adjustment_details: Annotated[
        Iterable[ClaimInformationOtherSubscriberInformationClaimLevelAdjustmentClaimAdjustmentDetail],
        PropertyInfo(alias="claimAdjustmentDetails"),
    ]


class ClaimInformationOtherSubscriberInformationMedicareInpatientAdjudication(TypedDict, total=False):
    covered_days_or_visits_count: Required[Annotated[str, PropertyInfo(alias="coveredDaysOrVisitsCount")]]

    capital_exception_amount: Annotated[str, PropertyInfo(alias="capitalExceptionAmount")]

    capital_hspdrg_amount: Annotated[str, PropertyInfo(alias="capitalHSPDRGAmount")]

    claim_disproportionate_share_amount: Annotated[str, PropertyInfo(alias="claimDisproportionateShareAmount")]

    claim_drg_amount: Annotated[str, PropertyInfo(alias="claimDRGAmount")]

    claim_indirect_teaching_amount: Annotated[str, PropertyInfo(alias="claimIndirectTeachingAmount")]

    claim_msp_pass_through_amount: Annotated[str, PropertyInfo(alias="claimMspPassThroughAmount")]

    claim_payment_remark_code: Annotated[List[str], PropertyInfo(alias="claimPaymentRemarkCode")]

    claim_pps_capital_amount: Annotated[str, PropertyInfo(alias="claimPpsCapitalAmount")]

    claim_pps_capital_outlier_ammount: Annotated[str, PropertyInfo(alias="claimPpsCapitalOutlierAmmount")]

    cost_report_day_count: Annotated[str, PropertyInfo(alias="costReportDayCount")]

    lifetime_psychiatric_days_count: Annotated[str, PropertyInfo(alias="lifetimePsychiatricDaysCount")]

    non_payable_professional_component_billed_amount: Annotated[
        str, PropertyInfo(alias="nonPayableProfessionalComponentBilledAmount")
    ]

    old_capital_amount: Annotated[str, PropertyInfo(alias="oldCapitalAmount")]

    pps_capital_dsh_drg_amount: Annotated[str, PropertyInfo(alias="ppsCapitalDshDrgAmount")]

    pps_capital_hsp_drg_amount: Annotated[str, PropertyInfo(alias="ppsCapitalHspDrgAmount")]

    pps_capital_ime_amount: Annotated[str, PropertyInfo(alias="ppsCapitalImeAmount")]

    pps_operating_federal_specific_drg_amount: Annotated[
        str, PropertyInfo(alias="ppsOperatingFederalSpecificDrgAmount")
    ]

    pps_operating_hospital_specific_drg_amount: Annotated[
        str, PropertyInfo(alias="ppsOperatingHospitalSpecificDrgAmount")
    ]


class ClaimInformationOtherSubscriberInformationMedicareOutpatientAdjudication(TypedDict, total=False):
    claim_payment_remark_code: Annotated[List[str], PropertyInfo(alias="claimPaymentRemarkCode")]

    end_stage_renal_disease_payment_amount: Annotated[str, PropertyInfo(alias="endStageRenalDiseasePaymentAmount")]

    hcpcs_payable_amount: Annotated[str, PropertyInfo(alias="hcpcsPayableAmount")]

    non_payable_professional_component_billed_amount: Annotated[
        str, PropertyInfo(alias="nonPayableProfessionalComponentBilledAmount")
    ]

    reimbursement_rate: Annotated[str, PropertyInfo(alias="reimbursementRate")]


class ClaimInformationOtherSubscriberInformationOtherPayerAttendingProviderOtherPayerAttendingProviderIdentifier(
    TypedDict, total=False
):
    identifier: Required[str]

    qualifier: Required[str]


class ClaimInformationOtherSubscriberInformationOtherPayerAttendingProvider(TypedDict, total=False):
    other_payer_attending_provider_identifier: Required[
        Annotated[
            Iterable[
                ClaimInformationOtherSubscriberInformationOtherPayerAttendingProviderOtherPayerAttendingProviderIdentifier
            ],
            PropertyInfo(alias="otherPayerAttendingProviderIdentifier"),
        ]
    ]


class ClaimInformationOtherSubscriberInformationOtherPayerBillingProviderOtherPayerBillingProviderIdentifier(
    TypedDict, total=False
):
    identifier: Required[str]

    qualifier: Required[str]


class ClaimInformationOtherSubscriberInformationOtherPayerBillingProvider(TypedDict, total=False):
    other_payer_billing_provider_identifier: Required[
        Annotated[
            Iterable[
                ClaimInformationOtherSubscriberInformationOtherPayerBillingProviderOtherPayerBillingProviderIdentifier
            ],
            PropertyInfo(alias="otherPayerBillingProviderIdentifier"),
        ]
    ]


class ClaimInformationOtherSubscriberInformationOtherPayerOperatingPhysicianOtherPayerOperatingPhysicianIdentifier(
    TypedDict, total=False
):
    identifier: Required[str]

    qualifier: Required[str]


class ClaimInformationOtherSubscriberInformationOtherPayerOperatingPhysician(TypedDict, total=False):
    other_payer_operating_physician_identifier: Required[
        Annotated[
            Iterable[
                ClaimInformationOtherSubscriberInformationOtherPayerOperatingPhysicianOtherPayerOperatingPhysicianIdentifier
            ],
            PropertyInfo(alias="otherPayerOperatingPhysicianIdentifier"),
        ]
    ]


class ClaimInformationOtherSubscriberInformationOtherPayerOtherOperatingPhysicianOtherPayerOtherOperatingPhysicianIdentifier(
    TypedDict, total=False
):
    identifier: Required[str]

    qualifier: Required[str]


class ClaimInformationOtherSubscriberInformationOtherPayerOtherOperatingPhysician(TypedDict, total=False):
    other_payer_other_operating_physician_identifier: Required[
        Annotated[
            Iterable[
                ClaimInformationOtherSubscriberInformationOtherPayerOtherOperatingPhysicianOtherPayerOtherOperatingPhysicianIdentifier
            ],
            PropertyInfo(alias="otherPayerOtherOperatingPhysicianIdentifier"),
        ]
    ]


class ClaimInformationOtherSubscriberInformationOtherPayerReferringProviderOtherPayerReferringProviderIdentifier(
    TypedDict, total=False
):
    identifier: Required[str]

    qualifier: Required[str]


class ClaimInformationOtherSubscriberInformationOtherPayerReferringProvider(TypedDict, total=False):
    other_payer_referring_provider_identifier: Required[
        Annotated[
            Iterable[
                ClaimInformationOtherSubscriberInformationOtherPayerReferringProviderOtherPayerReferringProviderIdentifier
            ],
            PropertyInfo(alias="otherPayerReferringProviderIdentifier"),
        ]
    ]


class ClaimInformationOtherSubscriberInformationOtherPayerRenderingProviderOtherPayerRenderingProviderIdentifier(
    TypedDict, total=False
):
    identifier: Required[str]

    qualifier: Required[str]


class ClaimInformationOtherSubscriberInformationOtherPayerRenderingProvider(TypedDict, total=False):
    other_payer_rendering_provider_identifier: Required[
        Annotated[
            Iterable[
                ClaimInformationOtherSubscriberInformationOtherPayerRenderingProviderOtherPayerRenderingProviderIdentifier
            ],
            PropertyInfo(alias="otherPayerRenderingProviderIdentifier"),
        ]
    ]


class ClaimInformationOtherSubscriberInformationOtherPayerServiceFacilityLocationOtherPayerServiceFacilityLocationIdentifier(
    TypedDict, total=False
):
    identifier: Required[str]

    qualifier: Required[str]


class ClaimInformationOtherSubscriberInformationOtherPayerServiceFacilityLocation(TypedDict, total=False):
    other_payer_service_facility_location_identifier: Required[
        Annotated[
            Iterable[
                ClaimInformationOtherSubscriberInformationOtherPayerServiceFacilityLocationOtherPayerServiceFacilityLocationIdentifier
            ],
            PropertyInfo(alias="otherPayerServiceFacilityLocationIdentifier"),
        ]
    ]


class ClaimInformationOtherSubscriberInformation(TypedDict, total=False):
    benefits_assignment_certification_indicator: Required[
        Annotated[Literal["N", "Y", "W"], PropertyInfo(alias="benefitsAssignmentCertificationIndicator")]
    ]

    claim_filing_indicator_code: Required[
        Annotated[
            Literal[
                "11",
                "12",
                "13",
                "14",
                "15",
                "16",
                "17",
                "AM",
                "BL",
                "CH",
                "DS",
                "FI",
                "HM",
                "LM",
                "MA",
                "MB",
                "MC",
                "OF",
                "TV",
                "VA",
                "WC",
                "ZZ",
            ],
            PropertyInfo(alias="claimFilingIndicatorCode"),
        ]
    ]

    individual_relationship_code: Required[
        Annotated[
            Literal["01", "18", "19", "20", "21", "39", "40", "53", "G8"],
            PropertyInfo(alias="individualRelationshipCode"),
        ]
    ]

    other_payer_name: Required[
        Annotated[ClaimInformationOtherSubscriberInformationOtherPayerName, PropertyInfo(alias="otherPayerName")]
    ]

    other_subscriber_name: Required[
        Annotated[
            ClaimInformationOtherSubscriberInformationOtherSubscriberName, PropertyInfo(alias="otherSubscriberName")
        ]
    ]

    payment_responsibility_level_code: Required[
        Annotated[
            Literal["A", "B", "C", "D", "E", "F", "G", "H", "P", "S", "T", "U"],
            PropertyInfo(alias="paymentResponsibilityLevelCode"),
        ]
    ]

    release_of_information_code: Required[Annotated[Literal["I", "Y"], PropertyInfo(alias="releaseOfInformationCode")]]

    claim_level_adjustments: Annotated[
        Iterable[ClaimInformationOtherSubscriberInformationClaimLevelAdjustment],
        PropertyInfo(alias="claimLevelAdjustments"),
    ]

    group_number: Annotated[str, PropertyInfo(alias="groupNumber")]

    medicare_inpatient_adjudication: Annotated[
        ClaimInformationOtherSubscriberInformationMedicareInpatientAdjudication,
        PropertyInfo(alias="medicareInpatientAdjudication"),
    ]

    medicare_outpatient_adjudication: Annotated[
        ClaimInformationOtherSubscriberInformationMedicareOutpatientAdjudication,
        PropertyInfo(alias="medicareOutpatientAdjudication"),
    ]

    non_covered_charge_amount: Annotated[str, PropertyInfo(alias="nonCoveredChargeAmount")]

    other_insured_group_name: Annotated[str, PropertyInfo(alias="otherInsuredGroupName")]

    other_payer_attending_provider: Annotated[
        ClaimInformationOtherSubscriberInformationOtherPayerAttendingProvider,
        PropertyInfo(alias="otherPayerAttendingProvider"),
    ]

    other_payer_billing_provider: Annotated[
        ClaimInformationOtherSubscriberInformationOtherPayerBillingProvider,
        PropertyInfo(alias="otherPayerBillingProvider"),
    ]

    other_payer_operating_physician: Annotated[
        ClaimInformationOtherSubscriberInformationOtherPayerOperatingPhysician,
        PropertyInfo(alias="otherPayerOperatingPhysician"),
    ]

    other_payer_other_operating_physician: Annotated[
        ClaimInformationOtherSubscriberInformationOtherPayerOtherOperatingPhysician,
        PropertyInfo(alias="otherPayerOtherOperatingPhysician"),
    ]

    other_payer_referring_provider: Annotated[
        ClaimInformationOtherSubscriberInformationOtherPayerReferringProvider,
        PropertyInfo(alias="otherPayerReferringProvider"),
    ]

    other_payer_rendering_provider: Annotated[
        ClaimInformationOtherSubscriberInformationOtherPayerRenderingProvider,
        PropertyInfo(alias="otherPayerRenderingProvider"),
    ]

    other_payer_service_facility_location: Annotated[
        ClaimInformationOtherSubscriberInformationOtherPayerServiceFacilityLocation,
        PropertyInfo(alias="otherPayerServiceFacilityLocation"),
    ]

    payer_paid_amount: Annotated[str, PropertyInfo(alias="payerPaidAmount")]

    policy_number: Annotated[str, PropertyInfo(alias="policyNumber")]

    remaining_patient_liability: Annotated[str, PropertyInfo(alias="remainingPatientLiability")]


class ClaimInformationPatientReasonForVisit(TypedDict, total=False):
    patient_reason_for_visit_code: Required[Annotated[str, PropertyInfo(alias="patientReasonForVisitCode")]]

    qualifier_code: Required[Annotated[Literal["APR", "PR"], PropertyInfo(alias="qualifierCode")]]


class ClaimInformationPrincipalProcedureInformation(TypedDict, total=False):
    principal_procedure_code: Required[Annotated[str, PropertyInfo(alias="principalProcedureCode")]]

    qualifier_code: Required[Annotated[Literal["BBR", "BR", "CAH"], PropertyInfo(alias="qualifierCode")]]

    principal_procedure_date: Annotated[str, PropertyInfo(alias="principalProcedureDate")]


class ClaimInformationServiceFacilityLocationAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ClaimInformationServiceFacilityLocation(TypedDict, total=False):
    address: Required[ClaimInformationServiceFacilityLocationAddress]

    organization_name: Required[Annotated[str, PropertyInfo(alias="organizationName")]]

    identification_code: Annotated[str, PropertyInfo(alias="identificationCode")]

    secondary_identification_qualifier_code: Annotated[
        Literal["0B", "G2", "LU"], PropertyInfo(alias="secondaryIdentificationQualifierCode")
    ]

    secondary_identifier: Annotated[str, PropertyInfo(alias="secondaryIdentifier")]


class ClaimInformationValueInformationList(TypedDict, total=False):
    value_code: Required[Annotated[str, PropertyInfo(alias="valueCode")]]

    value_code_amount: Required[Annotated[str, PropertyInfo(alias="valueCodeAmount")]]


class ClaimInformation(TypedDict, total=False):
    benefits_assignment_certification_indicator: Required[
        Annotated[Literal["N", "W", "Y"], PropertyInfo(alias="benefitsAssignmentCertificationIndicator")]
    ]

    claim_charge_amount: Required[Annotated[str, PropertyInfo(alias="claimChargeAmount")]]

    claim_code_information: Required[
        Annotated[ClaimInformationClaimCodeInformation, PropertyInfo(alias="claimCodeInformation")]
    ]

    claim_date_information: Required[
        Annotated[ClaimInformationClaimDateInformation, PropertyInfo(alias="claimDateInformation")]
    ]

    claim_filing_code: Required[
        Annotated[
            Literal[
                "11",
                "12",
                "13",
                "14",
                "15",
                "16",
                "17",
                "AM",
                "BL",
                "CH",
                "CI",
                "DS",
                "FI",
                "HM",
                "LM",
                "MA",
                "MB",
                "MC",
                "OF",
                "TV",
                "VA",
                "WC",
                "ZZ",
            ],
            PropertyInfo(alias="claimFilingCode"),
        ]
    ]

    claim_frequency_code: Required[Annotated[str, PropertyInfo(alias="claimFrequencyCode")]]

    place_of_service_code: Required[Annotated[str, PropertyInfo(alias="placeOfServiceCode")]]

    plan_participation_code: Required[Annotated[Literal["A", "B", "C"], PropertyInfo(alias="planParticipationCode")]]

    principal_diagnosis: Required[
        Annotated[ClaimInformationPrincipalDiagnosis, PropertyInfo(alias="principalDiagnosis")]
    ]

    release_information_code: Required[Annotated[Literal["I", "Y"], PropertyInfo(alias="releaseInformationCode")]]

    service_lines: Required[Annotated[Iterable[ClaimInformationServiceLine], PropertyInfo(alias="serviceLines")]]

    admitting_diagnosis: Annotated[ClaimInformationAdmittingDiagnosis, PropertyInfo(alias="admittingDiagnosis")]

    billing_note: Annotated[str, PropertyInfo(alias="billingNote")]

    claim_contract_information: Annotated[
        ClaimInformationClaimContractInformation, PropertyInfo(alias="claimContractInformation")
    ]

    claim_notes: Annotated[ClaimInformationClaimNotes, PropertyInfo(alias="claimNotes")]

    claim_pricing_information: Annotated[
        ClaimInformationClaimPricingInformation, PropertyInfo(alias="claimPricingInformation")
    ]

    claim_supplemental_information: Annotated[
        ClaimInformationClaimSupplementalInformation, PropertyInfo(alias="claimSupplementalInformation")
    ]

    condition_codes: Annotated[List[Literal["AV", "NU", "S2", "ST"]], PropertyInfo(alias="conditionCodes")]

    condition_codes_list: Annotated[
        Iterable[Iterable[ClaimInformationConditionCodesList]], PropertyInfo(alias="conditionCodesList")
    ]

    delay_reason_code: Annotated[
        Literal["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "15"], PropertyInfo(alias="delayReasonCode")
    ]

    diagnosis_related_group_information: Annotated[
        ClaimInformationDiagnosisRelatedGroupInformation, PropertyInfo(alias="diagnosisRelatedGroupInformation")
    ]

    epsdt_referral: Annotated[ClaimInformationEpsdtReferral, PropertyInfo(alias="epsdtReferral")]

    external_cause_of_injuries: Annotated[
        Iterable[ClaimInformationExternalCauseOfInjury], PropertyInfo(alias="externalCauseOfInjuries")
    ]

    file_information: Annotated[List[str], PropertyInfo(alias="fileInformation")]

    occurrence_information_list: Annotated[
        Iterable[Iterable[ClaimInformationOccurrenceInformationList]], PropertyInfo(alias="occurrenceInformationList")
    ]

    occurrence_span_informations: Annotated[
        Iterable[Iterable[ClaimInformationOccurrenceSpanInformation]], PropertyInfo(alias="occurrenceSpanInformations")
    ]

    other_diagnosis_information_list: Annotated[
        Iterable[Iterable[ClaimInformationOtherDiagnosisInformationList]],
        PropertyInfo(alias="otherDiagnosisInformationList"),
    ]

    other_procedure_information_list: Annotated[
        Iterable[Iterable[ClaimInformationOtherProcedureInformationList]],
        PropertyInfo(alias="otherProcedureInformationList"),
    ]

    other_subscriber_information: Annotated[
        ClaimInformationOtherSubscriberInformation, PropertyInfo(alias="otherSubscriberInformation")
    ]

    patient_amount_paid: Annotated[str, PropertyInfo(alias="patientAmountPaid")]

    patient_estimated_amount_due: Annotated[str, PropertyInfo(alias="patientEstimatedAmountDue")]

    patient_reason_for_visits: Annotated[
        Iterable[ClaimInformationPatientReasonForVisit], PropertyInfo(alias="patientReasonForVisits")
    ]

    patient_weight: Annotated[str, PropertyInfo(alias="patientWeight")]

    principal_procedure_information: Annotated[
        ClaimInformationPrincipalProcedureInformation, PropertyInfo(alias="principalProcedureInformation")
    ]

    property_casualty_claim_number: Annotated[str, PropertyInfo(alias="propertyCasualtyClaimNumber")]

    service_facility_location: Annotated[
        ClaimInformationServiceFacilityLocation, PropertyInfo(alias="serviceFacilityLocation")
    ]

    signature_indicator: Annotated[str, PropertyInfo(alias="signatureIndicator")]

    treatment_code_information_list: Annotated[Iterable[List[str]], PropertyInfo(alias="treatmentCodeInformationList")]

    value_information_list: Annotated[
        Iterable[Iterable[ClaimInformationValueInformationList]], PropertyInfo(alias="valueInformationList")
    ]


class Receiver(TypedDict, total=False):
    organization_name: Required[Annotated[str, PropertyInfo(alias="organizationName")]]

    tax_id: Annotated[str, PropertyInfo(alias="taxId")]


class SubmitterContactInformation(TypedDict, total=False):
    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    name: str

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]

    valid_contact: Annotated[bool, PropertyInfo(alias="validContact")]


class Submitter(TypedDict, total=False):
    contact_information: Required[Annotated[SubmitterContactInformation, PropertyInfo(alias="contactInformation")]]

    organization_name: Required[Annotated[str, PropertyInfo(alias="organizationName")]]

    tax_id: Required[Annotated[str, PropertyInfo(alias="taxId")]]


class SubscriberAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class Subscriber(TypedDict, total=False):
    first_name: Required[Annotated[str, PropertyInfo(alias="firstName")]]

    last_name: Required[Annotated[str, PropertyInfo(alias="lastName")]]

    payment_responsibility_level_code: Required[
        Annotated[
            Literal["A", "B", "C", "D", "E", "F", "G", "H", "P", "S", "T", "U"],
            PropertyInfo(alias="paymentResponsibilityLevelCode"),
        ]
    ]

    address: SubscriberAddress

    date_of_birth: Annotated[str, PropertyInfo(alias="dateOfBirth")]

    gender: Literal["M", "F", "U"]

    group_number: Annotated[str, PropertyInfo(alias="groupNumber")]

    member_id: Annotated[str, PropertyInfo(alias="memberId")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    policy_number: Annotated[str, PropertyInfo(alias="policyNumber")]

    ssn: str

    standard_health_id: Annotated[str, PropertyInfo(alias="standardHealthId")]

    suffix: str


class AttendingAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class AttendingContactInformation(TypedDict, total=False):
    name: Required[str]

    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]

    valid_contact: Annotated[bool, PropertyInfo(alias="validContact")]


class Attending(TypedDict, total=False):
    address: AttendingAddress

    contact_information: Annotated[AttendingContactInformation, PropertyInfo(alias="contactInformation")]

    employer_id: Annotated[str, PropertyInfo(alias="employerId")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    provider_type: Annotated[str, PropertyInfo(alias="providerType")]

    secondary_identification_qualifier_code: Annotated[
        Literal["0B", "1G", "G2", "LU"], PropertyInfo(alias="secondaryIdentificationQualifierCode")
    ]

    secondary_identifier: Annotated[str, PropertyInfo(alias="secondaryIdentifier")]

    suffix: str

    taxonomy_code: Annotated[str, PropertyInfo(alias="taxonomyCode")]


class BillingAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class BillingContactInformation(TypedDict, total=False):
    name: Required[str]

    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]

    valid_contact: Annotated[bool, PropertyInfo(alias="validContact")]


class Billing(TypedDict, total=False):
    address: Required[BillingAddress]

    employer_id: Required[Annotated[str, PropertyInfo(alias="employerId")]]

    npi: Required[str]

    commercial_number: Annotated[str, PropertyInfo(alias="commercialNumber")]

    contact_information: Annotated[BillingContactInformation, PropertyInfo(alias="contactInformation")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    location_number: Annotated[str, PropertyInfo(alias="locationNumber")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    provider_type: Annotated[Literal["BillingProvider"], PropertyInfo(alias="providerType")]

    provider_upin_number: Annotated[str, PropertyInfo(alias="providerUpinNumber")]

    secondary_identification_qualifier_code: Annotated[
        Literal["0B", "1G", "G2", "LU"], PropertyInfo(alias="secondaryIdentificationQualifierCode")
    ]

    secondary_identifier: Annotated[str, PropertyInfo(alias="secondaryIdentifier")]

    state_license_number: Annotated[str, PropertyInfo(alias="stateLicenseNumber")]

    suffix: str

    taxonomy_code: Annotated[str, PropertyInfo(alias="taxonomyCode")]


class BillingPayToAddressNameAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class BillingPayToAddressName(TypedDict, total=False):
    address: Required[BillingPayToAddressNameAddress]

    entity_type_qualifier: Required[Annotated[Literal["2"], PropertyInfo(alias="entityTypeQualifier")]]


class BillingPayToPlanNameAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class BillingPayToPlanName(TypedDict, total=False):
    identification_code: Required[Annotated[str, PropertyInfo(alias="identificationCode")]]

    identification_code_qualifier: Required[
        Annotated[Literal["PI", "XV"], PropertyInfo(alias="identificationCodeQualifier")]
    ]

    organization_name: Required[Annotated[str, PropertyInfo(alias="organizationName")]]

    tax_id: Required[Annotated[str, PropertyInfo(alias="taxId")]]

    address: BillingPayToPlanNameAddress

    claim_office_number: Annotated[str, PropertyInfo(alias="claimOfficeNumber")]

    naic: str

    payer_identification_number: Annotated[str, PropertyInfo(alias="payerIdentificationNumber")]


class DependentAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class Dependent(TypedDict, total=False):
    date_of_birth: Required[Annotated[str, PropertyInfo(alias="dateOfBirth")]]

    first_name: Required[Annotated[str, PropertyInfo(alias="firstName")]]

    gender: Required[Literal["M", "F", "U"]]

    last_name: Required[Annotated[str, PropertyInfo(alias="lastName")]]

    relationship_to_subscriber_code: Required[
        Annotated[
            Literal["01", "19", "20", "21", "39", "40", "53", "G8"], PropertyInfo(alias="relationshipToSubscriberCode")
        ]
    ]

    address: DependentAddress

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    ssn: str

    suffix: str


class EventMapping(TypedDict, total=False):
    received_277_ca: Annotated[str, PropertyInfo(alias="RECEIVED_277CA")]
    """A success event ID for the 277CA transaction"""


class OperatingPhysician(TypedDict, total=False):
    last_name: Required[Annotated[str, PropertyInfo(alias="lastName")]]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    identification_qualifier_code: Annotated[
        Literal["0B", "1G", "G2", "LU"], PropertyInfo(alias="identificationQualifierCode")
    ]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    secondary_identifier: Annotated[str, PropertyInfo(alias="secondaryIdentifier")]

    suffix: str


class OtherOperatingPhysician(TypedDict, total=False):
    last_name: Required[Annotated[str, PropertyInfo(alias="lastName")]]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    identification_qualifier_code: Annotated[
        Literal["0B", "1G", "G2", "LU"], PropertyInfo(alias="identificationQualifierCode")
    ]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    secondary_identifier: Annotated[str, PropertyInfo(alias="secondaryIdentifier")]

    suffix: str


class PayerAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ProviderAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ProviderContactInformation(TypedDict, total=False):
    name: Required[str]

    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]

    valid_contact: Annotated[bool, PropertyInfo(alias="validContact")]


class Provider(TypedDict, total=False):
    provider_type: Required[
        Annotated[
            Literal["BillingProvider", "AttendingProvider", "ReferringProvider", "RenderingProvider"],
            PropertyInfo(alias="providerType"),
        ]
    ]

    address: ProviderAddress

    contact_information: Annotated[ProviderContactInformation, PropertyInfo(alias="contactInformation")]

    employer_id: Annotated[str, PropertyInfo(alias="employerId")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    secondary_identification_qualifier_code: Annotated[
        Literal["0B", "1G", "G2", "LU"], PropertyInfo(alias="secondaryIdentificationQualifierCode")
    ]

    secondary_identifier: Annotated[str, PropertyInfo(alias="secondaryIdentifier")]

    suffix: str

    taxonomy_code: Annotated[str, PropertyInfo(alias="taxonomyCode")]


class ReferringAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ReferringContactInformation(TypedDict, total=False):
    name: Required[str]

    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]

    valid_contact: Annotated[bool, PropertyInfo(alias="validContact")]


class Referring(TypedDict, total=False):
    last_name: Required[Annotated[str, PropertyInfo(alias="lastName")]]

    address: ReferringAddress

    commercial_number: Annotated[str, PropertyInfo(alias="commercialNumber")]

    contact_information: Annotated[ReferringContactInformation, PropertyInfo(alias="contactInformation")]

    employer_id: Annotated[str, PropertyInfo(alias="employerId")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    location_number: Annotated[str, PropertyInfo(alias="locationNumber")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    provider_type: Annotated[Literal["ReferringProvider"], PropertyInfo(alias="providerType")]

    provider_upin_number: Annotated[str, PropertyInfo(alias="providerUpinNumber")]

    secondary_identification_qualifier_code: Annotated[
        Literal["0B", "1G", "G2"], PropertyInfo(alias="secondaryIdentificationQualifierCode")
    ]

    secondary_identifier: Annotated[str, PropertyInfo(alias="secondaryIdentifier")]

    state_license_number: Annotated[str, PropertyInfo(alias="stateLicenseNumber")]

    suffix: str

    taxonomy_code: Annotated[str, PropertyInfo(alias="taxonomyCode")]


class RenderingAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class RenderingContactInformation(TypedDict, total=False):
    name: Required[str]

    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]

    valid_contact: Annotated[bool, PropertyInfo(alias="validContact")]


class Rendering(TypedDict, total=False):
    last_name: Required[Annotated[str, PropertyInfo(alias="lastName")]]

    address: RenderingAddress

    commercial_number: Annotated[str, PropertyInfo(alias="commercialNumber")]

    contact_information: Annotated[RenderingContactInformation, PropertyInfo(alias="contactInformation")]

    employer_id: Annotated[str, PropertyInfo(alias="employerId")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    location_number: Annotated[str, PropertyInfo(alias="locationNumber")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    provider_type: Annotated[str, PropertyInfo(alias="providerType")]

    provider_upin_number: Annotated[str, PropertyInfo(alias="providerUpinNumber")]

    secondary_identification_qualifier_code: Annotated[
        Literal["0B", "1G", "G2", "LU"], PropertyInfo(alias="secondaryIdentificationQualifierCode")
    ]

    secondary_identifier: Annotated[str, PropertyInfo(alias="secondaryIdentifier")]

    state_license_number: Annotated[str, PropertyInfo(alias="stateLicenseNumber")]

    suffix: str

    taxonomy_code: Annotated[str, PropertyInfo(alias="taxonomyCode")]
