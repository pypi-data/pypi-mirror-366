# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.clearinghouse import ClaimSubmitResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClaim:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_cancel(self, client: SampleHealthcare) -> None:
        claim = client.v2.clearinghouse.claim.cancel(
            "claimId",
        )
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_cancel(self, client: SampleHealthcare) -> None:
        response = client.v2.clearinghouse.claim.with_raw_response.cancel(
            "claimId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        claim = response.parse()
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_cancel(self, client: SampleHealthcare) -> None:
        with client.v2.clearinghouse.claim.with_streaming_response.cancel(
            "claimId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            claim = response.parse()
            assert_matches_type(object, claim, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_cancel(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `claim_id` but received ''"):
            client.v2.clearinghouse.claim.with_raw_response.cancel(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_status(self, client: SampleHealthcare) -> None:
        claim = client.v2.clearinghouse.claim.retrieve_status(
            "claimId",
        )
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_status(self, client: SampleHealthcare) -> None:
        response = client.v2.clearinghouse.claim.with_raw_response.retrieve_status(
            "claimId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        claim = response.parse()
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_status(self, client: SampleHealthcare) -> None:
        with client.v2.clearinghouse.claim.with_streaming_response.retrieve_status(
            "claimId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            claim = response.parse()
            assert_matches_type(object, claim, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve_status(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `claim_id` but received ''"):
            client.v2.clearinghouse.claim.with_raw_response.retrieve_status(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_submit(self, client: SampleHealthcare) -> None:
        claim = client.v2.clearinghouse.claim.submit(
            claim_information={
                "benefits_assignment_certification_indicator": "N",
                "claim_charge_amount": "321669910225",
                "claim_code_information": {
                    "admission_type_code": "x",
                    "patient_status_code": "x",
                },
                "claim_date_information": {
                    "statement_begin_date": "73210630",
                    "statement_end_date": "73210630",
                },
                "claim_filing_code": "11",
                "claim_frequency_code": "x",
                "place_of_service_code": "xx",
                "plan_participation_code": "A",
                "principal_diagnosis": {
                    "principal_diagnosis_code": "principalDiagnosisCode",
                    "qualifier_code": "ABK",
                },
                "release_information_code": "I",
                "service_lines": [
                    {
                        "institutional_service": {
                            "line_item_charge_amount": "321669910225",
                            "measurement_unit": "DA",
                            "service_line_revenue_code": "serviceLineRevenueCode",
                            "service_unit_count": "serviceUnitCount",
                        }
                    }
                ],
            },
            idempotency_key="idempotencyKey",
            is_testing=True,
            receiver={"organization_name": "organizationName"},
            submitter={
                "contact_information": {},
                "organization_name": "organizationName",
                "tax_id": "xx",
            },
            subscriber={
                "first_name": "firstName",
                "last_name": "lastName",
                "payment_responsibility_level_code": "A",
            },
            trading_partner_service_id="tradingPartnerServiceId",
        )
        assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_submit_with_all_params(self, client: SampleHealthcare) -> None:
        claim = client.v2.clearinghouse.claim.submit(
            claim_information={
                "benefits_assignment_certification_indicator": "N",
                "claim_charge_amount": "321669910225",
                "claim_code_information": {
                    "admission_type_code": "x",
                    "patient_status_code": "x",
                    "admission_source_code": "admissionSourceCode",
                },
                "claim_date_information": {
                    "statement_begin_date": "73210630",
                    "statement_end_date": "73210630",
                    "admission_date_and_hour": "32160805",
                    "discharge_hour": "2029",
                    "repricer_received_date": "73210630",
                },
                "claim_filing_code": "11",
                "claim_frequency_code": "x",
                "place_of_service_code": "xx",
                "plan_participation_code": "A",
                "principal_diagnosis": {
                    "principal_diagnosis_code": "principalDiagnosisCode",
                    "qualifier_code": "ABK",
                    "present_on_admission_indicator": "N",
                },
                "release_information_code": "I",
                "service_lines": [
                    {
                        "institutional_service": {
                            "line_item_charge_amount": "321669910225",
                            "measurement_unit": "DA",
                            "service_line_revenue_code": "serviceLineRevenueCode",
                            "service_unit_count": "serviceUnitCount",
                            "description": "description",
                            "non_covered_charge_amount": "321669910225",
                            "procedure_code": "procedureCode",
                            "procedure_identifier": "ER",
                            "procedure_modifiers": ["string"],
                        },
                        "adjusted_repriced_line_item_reference_number": "adjustedRepricedLineItemReferenceNumber",
                        "assigned_number": "090",
                        "description": "description",
                        "drug_identification": {
                            "measurement_unit_code": "F2",
                            "national_drug_code": "nationalDrugCode",
                            "national_drug_unit_count": "321669910225",
                            "link_sequence_number": "linkSequenceNumber",
                            "pharmacy_prescription_number": "pharmacyPrescriptionNumber",
                        },
                        "facility_tax_amount": "321669910225",
                        "line_adjudication_information": [
                            {
                                "adjudication_or_payment_date": "73210630",
                                "other_payer_primary_identifier": "xx",
                                "paid_service_unit_count": "32166991",
                                "service_line_paid_amount": "321669910225",
                                "service_line_revenue_code": "serviceLineRevenueCode",
                                "bundled_line_number": "321669",
                                "line_adjustment": [
                                    {
                                        "adjustment_group_code": "CO",
                                        "claim_adjustment_details": [
                                            {
                                                "adjustment_amount": "adjustmentAmount",
                                                "adjustment_reason_code": "adjustmentReasonCode",
                                                "adjustment_quantity": "adjustmentQuantity",
                                            }
                                        ],
                                    }
                                ],
                                "procedure_code": "procedureCode",
                                "procedure_code_description": "procedureCodeDescription",
                                "procedure_modifier": ["string"],
                                "product_or_service_id_qualifier": "ER",
                                "remaining_patient_liability": "321669910225",
                            }
                        ],
                        "line_adjustment_information": {
                            "claim_paid_date": "73210630",
                            "other_payer_primary_identifier": "xx",
                            "paid_service_unit_count": "32166991",
                            "procedure_code": "procedureCode",
                            "remaining_patient_liability": "321669910225",
                            "service_id_qualifier": "ER",
                            "service_line_paid_amount": "321669910225",
                            "bundled_or_unbundled_line_number": "321669",
                            "claim_adjustment": {
                                "adjustment_group_code": "CO",
                                "claim_adjustment_details": [
                                    {
                                        "adjustment_amount": "adjustmentAmount",
                                        "adjustment_reason_code": "adjustmentReasonCode",
                                        "adjustment_quantity": "adjustmentQuantity",
                                    }
                                ],
                            },
                            "procedure_code_description": "procedureCodeDescription",
                            "procedure_modifiers": ["string"],
                        },
                        "line_note_text": "lineNoteText",
                        "line_pricing_information": {
                            "pricing_methodology_code": "00",
                            "repriced_allowed_amount": "321669910225",
                            "apg_amount": "321669910225",
                            "apg_code": "apgCode",
                            "exception_code": "1",
                            "flat_rate_amount": "321669910225",
                            "measurement_unit_code": "DA",
                            "policy_compliance_code": "1",
                            "reject_reason_code": "T1",
                            "repriced_approved_hcpcs_code": "repricedApprovedHCPCSCode",
                            "repriced_approved_service_unit_count": "32166991",
                            "repriced_organization_identifier": "repricedOrganizationIdentifier",
                            "repriced_saving_amount": "321669910225",
                            "service_id_qualifier": "ER",
                        },
                        "line_repricing_information": {
                            "pricing_methodology_code": "00",
                            "repriced_allowed_amount": "repricedAllowedAmount",
                            "exception_code": "1",
                            "policy_compliance_code": "1",
                            "product_or_service_id_qualifier": "ER",
                            "reject_reason_code": "T1",
                            "repriced_approved_amount": "repricedApprovedAmount",
                            "repriced_approved_drg_code": "repricedApprovedDRGCode",
                            "repriced_approved_hcpcs_code": "repricedApprovedHCPCSCode",
                            "repriced_approved_revenue_code": "repricedApprovedRevenueCode",
                            "repriced_approved_service_unit_code": "DA",
                            "repriced_approved_service_unit_count": "repricedApprovedServiceUnitCount",
                            "repriced_org_identifier": "repricedOrgIdentifier",
                            "repriced_per_diem": "repricedPerDiem",
                            "repriced_saving_amount": "repricedSavingAmount",
                        },
                        "line_supplement_information": {
                            "adjusted_repriced_claim_ref_number": "adjustedRepricedClaimRefNumber",
                            "auto_accident_state": "autoAccidentState",
                            "claim_control_number": "claimControlNumber",
                            "claim_number": "claimNumber",
                            "demo_project_identifier": "demoProjectIdentifier",
                            "investigational_device_exemption_number": "investigationalDeviceExemptionNumber",
                            "medical_record_number": "medicalRecordNumber",
                            "peer_review_authorization_number": "peerReviewAuthorizationNumber",
                            "prior_authorization_number": "priorAuthorizationNumber",
                            "referral_number": "referralNumber",
                            "report_information": {
                                "attachment_control_number": "xx",
                                "attachment_report_type_code": "03",
                                "attachment_transmission_code": "AA",
                            },
                            "report_informations": [
                                {
                                    "attachment_control_number": "xx",
                                    "attachment_report_type_code": "03",
                                    "attachment_transmission_code": "AA",
                                }
                            ],
                            "repriced_claim_number": "repricedClaimNumber",
                            "service_authorization_exception_code": "1",
                        },
                        "operating_physician": {
                            "last_name": "lastName",
                            "first_name": "firstName",
                            "identification_qualifier_code": "0B",
                            "middle_name": "middleName",
                            "npi": "7321669910",
                            "organization_name": "organizationName",
                            "secondary_identifier": "secondaryIdentifier",
                            "suffix": "suffix",
                        },
                        "other_operating_physician": {
                            "last_name": "lastName",
                            "first_name": "firstName",
                            "identification_qualifier_code": "0B",
                            "middle_name": "middleName",
                            "npi": "7321669910",
                            "organization_name": "organizationName",
                            "secondary_identifier": "secondaryIdentifier",
                            "suffix": "suffix",
                        },
                        "referring_provider": {
                            "address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "xx",
                                "country_sub_division_code": "x",
                                "postal_code": "xxx",
                                "state": "xx",
                            },
                            "commercial_number": "commercialNumber",
                            "contact_information": {
                                "name": "name",
                                "email": "email",
                                "fax_number": "faxNumber",
                                "phone_number": "phoneNumber",
                                "valid_contact": True,
                            },
                            "employer_id": "employerId",
                            "first_name": "firstName",
                            "last_name": "lastName",
                            "location_number": "locationNumber",
                            "middle_name": "middleName",
                            "npi": "7321669910",
                            "organization_name": "organizationName",
                            "provider_type": "ReferringProvider",
                            "provider_upin_number": "providerUpinNumber",
                            "reference_identification": [
                                {
                                    "identifier": "identifier",
                                    "qualifier": "qualifier",
                                }
                            ],
                            "secondary_identification_qualifier_code": "0B",
                            "secondary_identifier": "secondaryIdentifier",
                            "state_license_number": "stateLicenseNumber",
                            "suffix": "suffix",
                            "taxonomy_code": "2E02VLfW09",
                        },
                        "rendering_provider": {
                            "address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "xx",
                                "country_sub_division_code": "x",
                                "postal_code": "xxx",
                                "state": "xx",
                            },
                            "commercial_number": "commercialNumber",
                            "contact_information": {
                                "name": "name",
                                "email": "email",
                                "fax_number": "faxNumber",
                                "phone_number": "phoneNumber",
                                "valid_contact": True,
                            },
                            "employer_id": "employerId",
                            "first_name": "firstName",
                            "last_name": "lastName",
                            "location_number": "locationNumber",
                            "middle_name": "middleName",
                            "npi": "7321669910",
                            "organization_name": "organizationName",
                            "provider_type": "RenderingProvider",
                            "provider_upin_number": "providerUpinNumber",
                            "reference_identification": [
                                {
                                    "identifier": "identifier",
                                    "qualifier": "qualifier",
                                }
                            ],
                            "secondary_identification_qualifier_code": "0B",
                            "secondary_identifier": "secondaryIdentifier",
                            "state_license_number": "stateLicenseNumber",
                            "suffix": "suffix",
                            "taxonomy_code": "2E02VLfW09",
                        },
                        "repriced_line_item_reference_number": "repricedLineItemReferenceNumber",
                        "service_date": "73210630",
                        "service_date_end": "73210630",
                        "service_line_date_information": {
                            "begin_service_date": "73210630",
                            "end_service_date": "73210630",
                            "service_date": "73210630",
                            "valid_date_information": True,
                        },
                        "service_line_reference_information": {"provider_control_number": "providerControlNumber"},
                        "service_line_supplemental_information": {
                            "attachment_report_type_code": "03",
                            "attachment_transmission_code": "AA",
                            "attachment_control_number": "attachmentControlNumber",
                        },
                        "service_line_supplemental_informations": [
                            {
                                "attachment_report_type_code": "03",
                                "attachment_transmission_code": "AA",
                                "attachment_control_number": "attachmentControlNumber",
                            }
                        ],
                        "service_tax_amount": "321669910225",
                        "third_party_organization_notes": "thirdPartyOrganizationNotes",
                    }
                ],
                "admitting_diagnosis": {
                    "admitting_diagnosis_code": "admittingDiagnosisCode",
                    "qualifier_code": "ABJ",
                },
                "billing_note": "billingNote",
                "claim_contract_information": {
                    "contract_type_code": "01",
                    "contract_amount": "321669910225",
                    "contract_code": "contractCode",
                    "contract_percentage": "contractPercentage",
                    "contract_version_identifier": "contractVersionIdentifier",
                    "terms_discount_percentage": "termsDiscountPercentage",
                },
                "claim_notes": {
                    "additional_information": ["string"],
                    "allergies": ["string"],
                    "diagnosis_description": ["string"],
                    "dme": ["string"],
                    "functional_limits_or_reason_homebound": ["string"],
                    "goal_rehab_or_discharge_plans": ["string"],
                    "medications": ["string"],
                    "nutritional_requirments": ["string"],
                    "orders_for_discip_lines_and_treatments": ["string"],
                    "reasons_patient_leaves_home": ["string"],
                    "safety_measures": ["string"],
                    "supplemental_plan_of_treatment": ["string"],
                    "times_and_reasons_patient_not_at_home": ["string"],
                    "unusual_home_or_social_env": ["string"],
                    "updated_information": ["string"],
                },
                "claim_pricing_information": {
                    "pricing_methodology_code": "00",
                    "repriced_allowed_amount": "repricedAllowedAmount",
                    "exception_code": "1",
                    "policy_compliance_code": "1",
                    "product_or_service_id_qualifier": "ER",
                    "reject_reason_code": "T1",
                    "repriced_approved_amount": "repricedApprovedAmount",
                    "repriced_approved_drg_code": "repricedApprovedDRGCode",
                    "repriced_approved_hcpcs_code": "repricedApprovedHCPCSCode",
                    "repriced_approved_revenue_code": "repricedApprovedRevenueCode",
                    "repriced_approved_service_unit_code": "DA",
                    "repriced_approved_service_unit_count": "repricedApprovedServiceUnitCount",
                    "repriced_org_identifier": "repricedOrgIdentifier",
                    "repriced_per_diem": "repricedPerDiem",
                    "repriced_saving_amount": "repricedSavingAmount",
                },
                "claim_supplemental_information": {
                    "adjusted_repriced_claim_ref_number": "adjustedRepricedClaimRefNumber",
                    "auto_accident_state": "autoAccidentState",
                    "claim_control_number": "claimControlNumber",
                    "claim_number": "claimNumber",
                    "demo_project_identifier": "demoProjectIdentifier",
                    "investigational_device_exemption_number": "investigationalDeviceExemptionNumber",
                    "medical_record_number": "medicalRecordNumber",
                    "peer_review_authorization_number": "peerReviewAuthorizationNumber",
                    "prior_authorization_number": "priorAuthorizationNumber",
                    "referral_number": "referralNumber",
                    "report_information": {
                        "attachment_control_number": "xx",
                        "attachment_report_type_code": "03",
                        "attachment_transmission_code": "AA",
                    },
                    "report_informations": [
                        {
                            "attachment_control_number": "xx",
                            "attachment_report_type_code": "03",
                            "attachment_transmission_code": "AA",
                        }
                    ],
                    "repriced_claim_number": "repricedClaimNumber",
                    "service_authorization_exception_code": "1",
                },
                "condition_codes": ["AV"],
                "condition_codes_list": [[{"condition_code": "conditionCode"}]],
                "delay_reason_code": "1",
                "diagnosis_related_group_information": {"drug_related_group_code": "drugRelatedGroupCode"},
                "epsdt_referral": {
                    "certification_condition_code_applies_indicator": "N",
                    "condition_codes": ["AV"],
                },
                "external_cause_of_injuries": [
                    {
                        "external_cause_of_injury": "externalCauseOfInjury",
                        "qualifier_code": "ABN",
                        "present_on_admission_indicator": "N",
                    }
                ],
                "file_information": ["string"],
                "occurrence_information_list": [
                    [
                        {
                            "occurrence_span_code": "occurrenceSpanCode",
                            "occurrence_span_code_date": "73210630",
                        }
                    ]
                ],
                "occurrence_span_informations": [
                    [
                        {
                            "occurrence_span_code": "occurrenceSpanCode",
                            "occurrence_span_code_end_date": "73210630",
                            "occurrence_span_code_start_date": "73210630",
                        }
                    ]
                ],
                "other_diagnosis_information_list": [
                    [
                        {
                            "other_diagnosis_code": "otherDiagnosisCode",
                            "qualifier_code": "ABF",
                            "present_on_admission_indicator": "N",
                        }
                    ]
                ],
                "other_procedure_information_list": [
                    [
                        {
                            "other_procedure_code": "otherProcedureCode",
                            "qualifier_code": "BBQ",
                            "other_procedure_date": "73210630",
                        }
                    ]
                ],
                "other_subscriber_information": {
                    "benefits_assignment_certification_indicator": "N",
                    "claim_filing_indicator_code": "11",
                    "individual_relationship_code": "01",
                    "other_payer_name": {
                        "other_payer_identifier": "otherPayerIdentifier",
                        "other_payer_identifier_type_code": "PI",
                        "other_payer_organization_name": "otherPayerOrganizationName",
                        "other_insured_additional_identifier": "otherInsuredAdditionalIdentifier",
                        "other_payer_address": {
                            "address1": "address1",
                            "city": "city",
                            "address2": "address2",
                            "country_code": "xx",
                            "country_sub_division_code": "x",
                            "postal_code": "xxx",
                            "state": "xx",
                        },
                        "other_payer_adjudication_or_payment_date": "otherPayerAdjudicationOrPaymentDate",
                        "other_payer_claim_adjustment_indicator": True,
                        "other_payer_claim_control_number": "otherPayerClaimControlNumber",
                        "other_payer_prior_authorization_number": "otherPayerPriorAuthorizationNumber",
                        "other_payer_prior_authorization_or_referral_number": "otherPayerPriorAuthorizationOrReferralNumber",
                        "other_payer_secondary_identifier": [
                            {
                                "identifier": "identifier",
                                "qualifier": "qualifier",
                            }
                        ],
                    },
                    "other_subscriber_name": {
                        "other_insured_identifier": "otherInsuredIdentifier",
                        "other_insured_identifier_type_code": "II",
                        "other_insured_last_name": "otherInsuredLastName",
                        "other_insured_qualifier": "1",
                        "address": {
                            "address1": "address1",
                            "city": "city",
                            "address2": "address2",
                            "country_code": "xx",
                            "country_sub_division_code": "x",
                            "postal_code": "xxx",
                            "state": "xx",
                        },
                        "first_name": "firstName",
                        "other_insured_additional_identifier": ["string"],
                        "other_insured_first_name": "otherInsuredFirstName",
                        "other_insured_middle_name": "otherInsuredMiddleName",
                        "other_insured_suffix": "otherInsuredSuffix",
                    },
                    "payment_responsibility_level_code": "A",
                    "release_of_information_code": "I",
                    "claim_level_adjustments": [
                        {
                            "adjustment_group_code": "CO",
                            "claim_adjustment_details": [
                                {
                                    "adjustment_amount": "adjustmentAmount",
                                    "adjustment_reason_code": "adjustmentReasonCode",
                                    "adjustment_quantity": "adjustmentQuantity",
                                }
                            ],
                        }
                    ],
                    "group_number": "groupNumber",
                    "medicare_inpatient_adjudication": {
                        "covered_days_or_visits_count": "coveredDaysOrVisitsCount",
                        "capital_exception_amount": "capitalExceptionAmount",
                        "capital_hspdrg_amount": "capitalHSPDRGAmount",
                        "claim_disproportionate_share_amount": "claimDisproportionateShareAmount",
                        "claim_drg_amount": "claimDRGAmount",
                        "claim_indirect_teaching_amount": "claimIndirectTeachingAmount",
                        "claim_msp_pass_through_amount": "claimMspPassThroughAmount",
                        "claim_payment_remark_code": ["string"],
                        "claim_pps_capital_amount": "claimPpsCapitalAmount",
                        "claim_pps_capital_outlier_ammount": "claimPpsCapitalOutlierAmmount",
                        "cost_report_day_count": "costReportDayCount",
                        "lifetime_psychiatric_days_count": "lifetimePsychiatricDaysCount",
                        "non_payable_professional_component_billed_amount": "nonPayableProfessionalComponentBilledAmount",
                        "old_capital_amount": "oldCapitalAmount",
                        "pps_capital_dsh_drg_amount": "ppsCapitalDshDrgAmount",
                        "pps_capital_hsp_drg_amount": "ppsCapitalHspDrgAmount",
                        "pps_capital_ime_amount": "ppsCapitalImeAmount",
                        "pps_operating_federal_specific_drg_amount": "ppsOperatingFederalSpecificDrgAmount",
                        "pps_operating_hospital_specific_drg_amount": "ppsOperatingHospitalSpecificDrgAmount",
                    },
                    "medicare_outpatient_adjudication": {
                        "claim_payment_remark_code": ["string"],
                        "end_stage_renal_disease_payment_amount": "321669910225",
                        "hcpcs_payable_amount": "321669910225",
                        "non_payable_professional_component_billed_amount": "321669910225",
                        "reimbursement_rate": "reimbursementRate",
                    },
                    "non_covered_charge_amount": "nonCoveredChargeAmount",
                    "other_insured_group_name": "otherInsuredGroupName",
                    "other_payer_attending_provider": {
                        "other_payer_attending_provider_identifier": [
                            {
                                "identifier": "identifier",
                                "qualifier": "qualifier",
                            }
                        ]
                    },
                    "other_payer_billing_provider": {
                        "other_payer_billing_provider_identifier": [
                            {
                                "identifier": "identifier",
                                "qualifier": "qualifier",
                            }
                        ]
                    },
                    "other_payer_operating_physician": {
                        "other_payer_operating_physician_identifier": [
                            {
                                "identifier": "identifier",
                                "qualifier": "qualifier",
                            }
                        ]
                    },
                    "other_payer_other_operating_physician": {
                        "other_payer_other_operating_physician_identifier": [
                            {
                                "identifier": "identifier",
                                "qualifier": "qualifier",
                            }
                        ]
                    },
                    "other_payer_referring_provider": {
                        "other_payer_referring_provider_identifier": [
                            {
                                "identifier": "identifier",
                                "qualifier": "qualifier",
                            }
                        ]
                    },
                    "other_payer_rendering_provider": {
                        "other_payer_rendering_provider_identifier": [
                            {
                                "identifier": "identifier",
                                "qualifier": "qualifier",
                            }
                        ]
                    },
                    "other_payer_service_facility_location": {
                        "other_payer_service_facility_location_identifier": [
                            {
                                "identifier": "identifier",
                                "qualifier": "qualifier",
                            }
                        ]
                    },
                    "payer_paid_amount": "payerPaidAmount",
                    "policy_number": "policyNumber",
                    "remaining_patient_liability": "remainingPatientLiability",
                },
                "patient_amount_paid": "patientAmountPaid",
                "patient_estimated_amount_due": "321669910225",
                "patient_reason_for_visits": [
                    {
                        "patient_reason_for_visit_code": "patientReasonForVisitCode",
                        "qualifier_code": "APR",
                    }
                ],
                "patient_weight": "patientWeight",
                "principal_procedure_information": {
                    "principal_procedure_code": "principalProcedureCode",
                    "qualifier_code": "BBR",
                    "principal_procedure_date": "73210630",
                },
                "property_casualty_claim_number": "propertyCasualtyClaimNumber",
                "service_facility_location": {
                    "address": {
                        "address1": "address1",
                        "city": "city",
                        "address2": "address2",
                        "country_code": "xx",
                        "country_sub_division_code": "x",
                        "postal_code": "xxx",
                        "state": "xx",
                    },
                    "organization_name": "organizationName",
                    "identification_code": "identificationCode",
                    "secondary_identification_qualifier_code": "0B",
                    "secondary_identifier": "secondaryIdentifier",
                },
                "signature_indicator": "signatureIndicator",
                "treatment_code_information_list": [["string"]],
                "value_information_list": [
                    [
                        {
                            "value_code": "valueCode",
                            "value_code_amount": "321669910225",
                        }
                    ]
                ],
            },
            idempotency_key="idempotencyKey",
            is_testing=True,
            receiver={
                "organization_name": "organizationName",
                "tax_id": "xx",
            },
            submitter={
                "contact_information": {
                    "email": "email",
                    "fax_number": "faxNumber",
                    "name": "name",
                    "phone_number": "phoneNumber",
                    "valid_contact": True,
                },
                "organization_name": "organizationName",
                "tax_id": "xx",
            },
            subscriber={
                "first_name": "firstName",
                "last_name": "lastName",
                "payment_responsibility_level_code": "A",
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "xx",
                    "country_sub_division_code": "x",
                    "postal_code": "xxx",
                    "state": "xx",
                },
                "date_of_birth": "73210630",
                "gender": "M",
                "group_number": "groupNumber",
                "member_id": "xx",
                "middle_name": "middleName",
                "policy_number": "policyNumber",
                "ssn": "732166991",
                "standard_health_id": "standardHealthId",
                "suffix": "suffix",
            },
            trading_partner_service_id="tradingPartnerServiceId",
            attending={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "xx",
                    "country_sub_division_code": "x",
                    "postal_code": "xxx",
                    "state": "xx",
                },
                "contact_information": {
                    "name": "name",
                    "email": "email",
                    "fax_number": "faxNumber",
                    "phone_number": "phoneNumber",
                    "valid_contact": True,
                },
                "employer_id": "employerId",
                "first_name": "firstName",
                "last_name": "lastName",
                "middle_name": "middleName",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "provider_type": "providerType",
                "secondary_identification_qualifier_code": "0B",
                "secondary_identifier": "secondaryIdentifier",
                "suffix": "suffix",
                "taxonomy_code": "2E02VLfW09",
            },
            billing={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "xx",
                    "country_sub_division_code": "x",
                    "postal_code": "xxx",
                    "state": "xx",
                },
                "employer_id": "employerId",
                "npi": "7321669910",
                "commercial_number": "commercialNumber",
                "contact_information": {
                    "name": "name",
                    "email": "email",
                    "fax_number": "faxNumber",
                    "phone_number": "phoneNumber",
                    "valid_contact": True,
                },
                "first_name": "firstName",
                "last_name": "lastName",
                "location_number": "locationNumber",
                "middle_name": "middleName",
                "organization_name": "organizationName",
                "provider_type": "BillingProvider",
                "provider_upin_number": "providerUpinNumber",
                "secondary_identification_qualifier_code": "0B",
                "secondary_identifier": "secondaryIdentifier",
                "state_license_number": "stateLicenseNumber",
                "suffix": "suffix",
                "taxonomy_code": "2E02VLfW09",
            },
            billing_pay_to_address_name={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "xx",
                    "country_sub_division_code": "x",
                    "postal_code": "xxx",
                    "state": "xx",
                },
                "entity_type_qualifier": "2",
            },
            billing_pay_to_plan_name={
                "identification_code": "xx",
                "identification_code_qualifier": "PI",
                "organization_name": "organizationName",
                "tax_id": "732166991",
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "xx",
                    "country_sub_division_code": "x",
                    "postal_code": "xxx",
                    "state": "xx",
                },
                "claim_office_number": "claimOfficeNumber",
                "naic": "73216",
                "payer_identification_number": "payerIdentificationNumber",
            },
            control_number="155771193",
            correlation_id="correlationId",
            dependent={
                "date_of_birth": "73210630",
                "first_name": "firstName",
                "gender": "M",
                "last_name": "lastName",
                "relationship_to_subscriber_code": "01",
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "xx",
                    "country_sub_division_code": "x",
                    "postal_code": "xxx",
                    "state": "xx",
                },
                "middle_name": "middleName",
                "ssn": "732166991",
                "suffix": "suffix",
            },
            event_mapping={"received_277_ca": "RECEIVED_277CA"},
            operating_physician={
                "last_name": "lastName",
                "first_name": "firstName",
                "identification_qualifier_code": "0B",
                "middle_name": "middleName",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "secondary_identifier": "secondaryIdentifier",
                "suffix": "suffix",
            },
            other_operating_physician={
                "last_name": "lastName",
                "first_name": "firstName",
                "identification_qualifier_code": "0B",
                "middle_name": "middleName",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "secondary_identifier": "secondaryIdentifier",
                "suffix": "suffix",
            },
            payer_address={
                "address1": "address1",
                "city": "city",
                "address2": "address2",
                "country_code": "xx",
                "country_sub_division_code": "x",
                "postal_code": "xxx",
                "state": "xx",
            },
            providers=[
                {
                    "provider_type": "BillingProvider",
                    "address": {
                        "address1": "address1",
                        "city": "city",
                        "address2": "address2",
                        "country_code": "xx",
                        "country_sub_division_code": "x",
                        "postal_code": "xxx",
                        "state": "xx",
                    },
                    "contact_information": {
                        "name": "name",
                        "email": "email",
                        "fax_number": "faxNumber",
                        "phone_number": "phoneNumber",
                        "valid_contact": True,
                    },
                    "employer_id": "employerId",
                    "first_name": "firstName",
                    "last_name": "lastName",
                    "middle_name": "middleName",
                    "npi": "7321669910",
                    "organization_name": "organizationName",
                    "secondary_identification_qualifier_code": "0B",
                    "secondary_identifier": "secondaryIdentifier",
                    "suffix": "suffix",
                    "taxonomy_code": "2E02VLfW09",
                }
            ],
            referring={
                "last_name": "lastName",
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "xx",
                    "country_sub_division_code": "x",
                    "postal_code": "xxx",
                    "state": "xx",
                },
                "commercial_number": "commercialNumber",
                "contact_information": {
                    "name": "name",
                    "email": "email",
                    "fax_number": "faxNumber",
                    "phone_number": "phoneNumber",
                    "valid_contact": True,
                },
                "employer_id": "employerId",
                "first_name": "firstName",
                "location_number": "locationNumber",
                "middle_name": "middleName",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "provider_type": "ReferringProvider",
                "provider_upin_number": "providerUpinNumber",
                "secondary_identification_qualifier_code": "0B",
                "secondary_identifier": "secondaryIdentifier",
                "state_license_number": "stateLicenseNumber",
                "suffix": "suffix",
                "taxonomy_code": "2E02VLfW09",
            },
            rendering={
                "last_name": "lastName",
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "xx",
                    "country_sub_division_code": "x",
                    "postal_code": "xxx",
                    "state": "xx",
                },
                "commercial_number": "commercialNumber",
                "contact_information": {
                    "name": "name",
                    "email": "email",
                    "fax_number": "faxNumber",
                    "phone_number": "phoneNumber",
                    "valid_contact": True,
                },
                "employer_id": "employerId",
                "first_name": "firstName",
                "location_number": "locationNumber",
                "middle_name": "middleName",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "provider_type": "providerType",
                "provider_upin_number": "providerUpinNumber",
                "secondary_identification_qualifier_code": "0B",
                "secondary_identifier": "secondaryIdentifier",
                "state_license_number": "stateLicenseNumber",
                "suffix": "suffix",
                "taxonomy_code": "2E02VLfW09",
            },
            trading_partner_name="tradingPartnerName",
        )
        assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_submit(self, client: SampleHealthcare) -> None:
        response = client.v2.clearinghouse.claim.with_raw_response.submit(
            claim_information={
                "benefits_assignment_certification_indicator": "N",
                "claim_charge_amount": "321669910225",
                "claim_code_information": {
                    "admission_type_code": "x",
                    "patient_status_code": "x",
                },
                "claim_date_information": {
                    "statement_begin_date": "73210630",
                    "statement_end_date": "73210630",
                },
                "claim_filing_code": "11",
                "claim_frequency_code": "x",
                "place_of_service_code": "xx",
                "plan_participation_code": "A",
                "principal_diagnosis": {
                    "principal_diagnosis_code": "principalDiagnosisCode",
                    "qualifier_code": "ABK",
                },
                "release_information_code": "I",
                "service_lines": [
                    {
                        "institutional_service": {
                            "line_item_charge_amount": "321669910225",
                            "measurement_unit": "DA",
                            "service_line_revenue_code": "serviceLineRevenueCode",
                            "service_unit_count": "serviceUnitCount",
                        }
                    }
                ],
            },
            idempotency_key="idempotencyKey",
            is_testing=True,
            receiver={"organization_name": "organizationName"},
            submitter={
                "contact_information": {},
                "organization_name": "organizationName",
                "tax_id": "xx",
            },
            subscriber={
                "first_name": "firstName",
                "last_name": "lastName",
                "payment_responsibility_level_code": "A",
            },
            trading_partner_service_id="tradingPartnerServiceId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        claim = response.parse()
        assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_submit(self, client: SampleHealthcare) -> None:
        with client.v2.clearinghouse.claim.with_streaming_response.submit(
            claim_information={
                "benefits_assignment_certification_indicator": "N",
                "claim_charge_amount": "321669910225",
                "claim_code_information": {
                    "admission_type_code": "x",
                    "patient_status_code": "x",
                },
                "claim_date_information": {
                    "statement_begin_date": "73210630",
                    "statement_end_date": "73210630",
                },
                "claim_filing_code": "11",
                "claim_frequency_code": "x",
                "place_of_service_code": "xx",
                "plan_participation_code": "A",
                "principal_diagnosis": {
                    "principal_diagnosis_code": "principalDiagnosisCode",
                    "qualifier_code": "ABK",
                },
                "release_information_code": "I",
                "service_lines": [
                    {
                        "institutional_service": {
                            "line_item_charge_amount": "321669910225",
                            "measurement_unit": "DA",
                            "service_line_revenue_code": "serviceLineRevenueCode",
                            "service_unit_count": "serviceUnitCount",
                        }
                    }
                ],
            },
            idempotency_key="idempotencyKey",
            is_testing=True,
            receiver={"organization_name": "organizationName"},
            submitter={
                "contact_information": {},
                "organization_name": "organizationName",
                "tax_id": "xx",
            },
            subscriber={
                "first_name": "firstName",
                "last_name": "lastName",
                "payment_responsibility_level_code": "A",
            },
            trading_partner_service_id="tradingPartnerServiceId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            claim = response.parse()
            assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncClaim:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_cancel(self, async_client: AsyncSampleHealthcare) -> None:
        claim = await async_client.v2.clearinghouse.claim.cancel(
            "claimId",
        )
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.clearinghouse.claim.with_raw_response.cancel(
            "claimId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        claim = await response.parse()
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.clearinghouse.claim.with_streaming_response.cancel(
            "claimId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            claim = await response.parse()
            assert_matches_type(object, claim, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `claim_id` but received ''"):
            await async_client.v2.clearinghouse.claim.with_raw_response.cancel(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_status(self, async_client: AsyncSampleHealthcare) -> None:
        claim = await async_client.v2.clearinghouse.claim.retrieve_status(
            "claimId",
        )
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_status(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.clearinghouse.claim.with_raw_response.retrieve_status(
            "claimId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        claim = await response.parse()
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_status(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.clearinghouse.claim.with_streaming_response.retrieve_status(
            "claimId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            claim = await response.parse()
            assert_matches_type(object, claim, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve_status(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `claim_id` but received ''"):
            await async_client.v2.clearinghouse.claim.with_raw_response.retrieve_status(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_submit(self, async_client: AsyncSampleHealthcare) -> None:
        claim = await async_client.v2.clearinghouse.claim.submit(
            claim_information={
                "benefits_assignment_certification_indicator": "N",
                "claim_charge_amount": "321669910225",
                "claim_code_information": {
                    "admission_type_code": "x",
                    "patient_status_code": "x",
                },
                "claim_date_information": {
                    "statement_begin_date": "73210630",
                    "statement_end_date": "73210630",
                },
                "claim_filing_code": "11",
                "claim_frequency_code": "x",
                "place_of_service_code": "xx",
                "plan_participation_code": "A",
                "principal_diagnosis": {
                    "principal_diagnosis_code": "principalDiagnosisCode",
                    "qualifier_code": "ABK",
                },
                "release_information_code": "I",
                "service_lines": [
                    {
                        "institutional_service": {
                            "line_item_charge_amount": "321669910225",
                            "measurement_unit": "DA",
                            "service_line_revenue_code": "serviceLineRevenueCode",
                            "service_unit_count": "serviceUnitCount",
                        }
                    }
                ],
            },
            idempotency_key="idempotencyKey",
            is_testing=True,
            receiver={"organization_name": "organizationName"},
            submitter={
                "contact_information": {},
                "organization_name": "organizationName",
                "tax_id": "xx",
            },
            subscriber={
                "first_name": "firstName",
                "last_name": "lastName",
                "payment_responsibility_level_code": "A",
            },
            trading_partner_service_id="tradingPartnerServiceId",
        )
        assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_submit_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        claim = await async_client.v2.clearinghouse.claim.submit(
            claim_information={
                "benefits_assignment_certification_indicator": "N",
                "claim_charge_amount": "321669910225",
                "claim_code_information": {
                    "admission_type_code": "x",
                    "patient_status_code": "x",
                    "admission_source_code": "admissionSourceCode",
                },
                "claim_date_information": {
                    "statement_begin_date": "73210630",
                    "statement_end_date": "73210630",
                    "admission_date_and_hour": "32160805",
                    "discharge_hour": "2029",
                    "repricer_received_date": "73210630",
                },
                "claim_filing_code": "11",
                "claim_frequency_code": "x",
                "place_of_service_code": "xx",
                "plan_participation_code": "A",
                "principal_diagnosis": {
                    "principal_diagnosis_code": "principalDiagnosisCode",
                    "qualifier_code": "ABK",
                    "present_on_admission_indicator": "N",
                },
                "release_information_code": "I",
                "service_lines": [
                    {
                        "institutional_service": {
                            "line_item_charge_amount": "321669910225",
                            "measurement_unit": "DA",
                            "service_line_revenue_code": "serviceLineRevenueCode",
                            "service_unit_count": "serviceUnitCount",
                            "description": "description",
                            "non_covered_charge_amount": "321669910225",
                            "procedure_code": "procedureCode",
                            "procedure_identifier": "ER",
                            "procedure_modifiers": ["string"],
                        },
                        "adjusted_repriced_line_item_reference_number": "adjustedRepricedLineItemReferenceNumber",
                        "assigned_number": "090",
                        "description": "description",
                        "drug_identification": {
                            "measurement_unit_code": "F2",
                            "national_drug_code": "nationalDrugCode",
                            "national_drug_unit_count": "321669910225",
                            "link_sequence_number": "linkSequenceNumber",
                            "pharmacy_prescription_number": "pharmacyPrescriptionNumber",
                        },
                        "facility_tax_amount": "321669910225",
                        "line_adjudication_information": [
                            {
                                "adjudication_or_payment_date": "73210630",
                                "other_payer_primary_identifier": "xx",
                                "paid_service_unit_count": "32166991",
                                "service_line_paid_amount": "321669910225",
                                "service_line_revenue_code": "serviceLineRevenueCode",
                                "bundled_line_number": "321669",
                                "line_adjustment": [
                                    {
                                        "adjustment_group_code": "CO",
                                        "claim_adjustment_details": [
                                            {
                                                "adjustment_amount": "adjustmentAmount",
                                                "adjustment_reason_code": "adjustmentReasonCode",
                                                "adjustment_quantity": "adjustmentQuantity",
                                            }
                                        ],
                                    }
                                ],
                                "procedure_code": "procedureCode",
                                "procedure_code_description": "procedureCodeDescription",
                                "procedure_modifier": ["string"],
                                "product_or_service_id_qualifier": "ER",
                                "remaining_patient_liability": "321669910225",
                            }
                        ],
                        "line_adjustment_information": {
                            "claim_paid_date": "73210630",
                            "other_payer_primary_identifier": "xx",
                            "paid_service_unit_count": "32166991",
                            "procedure_code": "procedureCode",
                            "remaining_patient_liability": "321669910225",
                            "service_id_qualifier": "ER",
                            "service_line_paid_amount": "321669910225",
                            "bundled_or_unbundled_line_number": "321669",
                            "claim_adjustment": {
                                "adjustment_group_code": "CO",
                                "claim_adjustment_details": [
                                    {
                                        "adjustment_amount": "adjustmentAmount",
                                        "adjustment_reason_code": "adjustmentReasonCode",
                                        "adjustment_quantity": "adjustmentQuantity",
                                    }
                                ],
                            },
                            "procedure_code_description": "procedureCodeDescription",
                            "procedure_modifiers": ["string"],
                        },
                        "line_note_text": "lineNoteText",
                        "line_pricing_information": {
                            "pricing_methodology_code": "00",
                            "repriced_allowed_amount": "321669910225",
                            "apg_amount": "321669910225",
                            "apg_code": "apgCode",
                            "exception_code": "1",
                            "flat_rate_amount": "321669910225",
                            "measurement_unit_code": "DA",
                            "policy_compliance_code": "1",
                            "reject_reason_code": "T1",
                            "repriced_approved_hcpcs_code": "repricedApprovedHCPCSCode",
                            "repriced_approved_service_unit_count": "32166991",
                            "repriced_organization_identifier": "repricedOrganizationIdentifier",
                            "repriced_saving_amount": "321669910225",
                            "service_id_qualifier": "ER",
                        },
                        "line_repricing_information": {
                            "pricing_methodology_code": "00",
                            "repriced_allowed_amount": "repricedAllowedAmount",
                            "exception_code": "1",
                            "policy_compliance_code": "1",
                            "product_or_service_id_qualifier": "ER",
                            "reject_reason_code": "T1",
                            "repriced_approved_amount": "repricedApprovedAmount",
                            "repriced_approved_drg_code": "repricedApprovedDRGCode",
                            "repriced_approved_hcpcs_code": "repricedApprovedHCPCSCode",
                            "repriced_approved_revenue_code": "repricedApprovedRevenueCode",
                            "repriced_approved_service_unit_code": "DA",
                            "repriced_approved_service_unit_count": "repricedApprovedServiceUnitCount",
                            "repriced_org_identifier": "repricedOrgIdentifier",
                            "repriced_per_diem": "repricedPerDiem",
                            "repriced_saving_amount": "repricedSavingAmount",
                        },
                        "line_supplement_information": {
                            "adjusted_repriced_claim_ref_number": "adjustedRepricedClaimRefNumber",
                            "auto_accident_state": "autoAccidentState",
                            "claim_control_number": "claimControlNumber",
                            "claim_number": "claimNumber",
                            "demo_project_identifier": "demoProjectIdentifier",
                            "investigational_device_exemption_number": "investigationalDeviceExemptionNumber",
                            "medical_record_number": "medicalRecordNumber",
                            "peer_review_authorization_number": "peerReviewAuthorizationNumber",
                            "prior_authorization_number": "priorAuthorizationNumber",
                            "referral_number": "referralNumber",
                            "report_information": {
                                "attachment_control_number": "xx",
                                "attachment_report_type_code": "03",
                                "attachment_transmission_code": "AA",
                            },
                            "report_informations": [
                                {
                                    "attachment_control_number": "xx",
                                    "attachment_report_type_code": "03",
                                    "attachment_transmission_code": "AA",
                                }
                            ],
                            "repriced_claim_number": "repricedClaimNumber",
                            "service_authorization_exception_code": "1",
                        },
                        "operating_physician": {
                            "last_name": "lastName",
                            "first_name": "firstName",
                            "identification_qualifier_code": "0B",
                            "middle_name": "middleName",
                            "npi": "7321669910",
                            "organization_name": "organizationName",
                            "secondary_identifier": "secondaryIdentifier",
                            "suffix": "suffix",
                        },
                        "other_operating_physician": {
                            "last_name": "lastName",
                            "first_name": "firstName",
                            "identification_qualifier_code": "0B",
                            "middle_name": "middleName",
                            "npi": "7321669910",
                            "organization_name": "organizationName",
                            "secondary_identifier": "secondaryIdentifier",
                            "suffix": "suffix",
                        },
                        "referring_provider": {
                            "address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "xx",
                                "country_sub_division_code": "x",
                                "postal_code": "xxx",
                                "state": "xx",
                            },
                            "commercial_number": "commercialNumber",
                            "contact_information": {
                                "name": "name",
                                "email": "email",
                                "fax_number": "faxNumber",
                                "phone_number": "phoneNumber",
                                "valid_contact": True,
                            },
                            "employer_id": "employerId",
                            "first_name": "firstName",
                            "last_name": "lastName",
                            "location_number": "locationNumber",
                            "middle_name": "middleName",
                            "npi": "7321669910",
                            "organization_name": "organizationName",
                            "provider_type": "ReferringProvider",
                            "provider_upin_number": "providerUpinNumber",
                            "reference_identification": [
                                {
                                    "identifier": "identifier",
                                    "qualifier": "qualifier",
                                }
                            ],
                            "secondary_identification_qualifier_code": "0B",
                            "secondary_identifier": "secondaryIdentifier",
                            "state_license_number": "stateLicenseNumber",
                            "suffix": "suffix",
                            "taxonomy_code": "2E02VLfW09",
                        },
                        "rendering_provider": {
                            "address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "xx",
                                "country_sub_division_code": "x",
                                "postal_code": "xxx",
                                "state": "xx",
                            },
                            "commercial_number": "commercialNumber",
                            "contact_information": {
                                "name": "name",
                                "email": "email",
                                "fax_number": "faxNumber",
                                "phone_number": "phoneNumber",
                                "valid_contact": True,
                            },
                            "employer_id": "employerId",
                            "first_name": "firstName",
                            "last_name": "lastName",
                            "location_number": "locationNumber",
                            "middle_name": "middleName",
                            "npi": "7321669910",
                            "organization_name": "organizationName",
                            "provider_type": "RenderingProvider",
                            "provider_upin_number": "providerUpinNumber",
                            "reference_identification": [
                                {
                                    "identifier": "identifier",
                                    "qualifier": "qualifier",
                                }
                            ],
                            "secondary_identification_qualifier_code": "0B",
                            "secondary_identifier": "secondaryIdentifier",
                            "state_license_number": "stateLicenseNumber",
                            "suffix": "suffix",
                            "taxonomy_code": "2E02VLfW09",
                        },
                        "repriced_line_item_reference_number": "repricedLineItemReferenceNumber",
                        "service_date": "73210630",
                        "service_date_end": "73210630",
                        "service_line_date_information": {
                            "begin_service_date": "73210630",
                            "end_service_date": "73210630",
                            "service_date": "73210630",
                            "valid_date_information": True,
                        },
                        "service_line_reference_information": {"provider_control_number": "providerControlNumber"},
                        "service_line_supplemental_information": {
                            "attachment_report_type_code": "03",
                            "attachment_transmission_code": "AA",
                            "attachment_control_number": "attachmentControlNumber",
                        },
                        "service_line_supplemental_informations": [
                            {
                                "attachment_report_type_code": "03",
                                "attachment_transmission_code": "AA",
                                "attachment_control_number": "attachmentControlNumber",
                            }
                        ],
                        "service_tax_amount": "321669910225",
                        "third_party_organization_notes": "thirdPartyOrganizationNotes",
                    }
                ],
                "admitting_diagnosis": {
                    "admitting_diagnosis_code": "admittingDiagnosisCode",
                    "qualifier_code": "ABJ",
                },
                "billing_note": "billingNote",
                "claim_contract_information": {
                    "contract_type_code": "01",
                    "contract_amount": "321669910225",
                    "contract_code": "contractCode",
                    "contract_percentage": "contractPercentage",
                    "contract_version_identifier": "contractVersionIdentifier",
                    "terms_discount_percentage": "termsDiscountPercentage",
                },
                "claim_notes": {
                    "additional_information": ["string"],
                    "allergies": ["string"],
                    "diagnosis_description": ["string"],
                    "dme": ["string"],
                    "functional_limits_or_reason_homebound": ["string"],
                    "goal_rehab_or_discharge_plans": ["string"],
                    "medications": ["string"],
                    "nutritional_requirments": ["string"],
                    "orders_for_discip_lines_and_treatments": ["string"],
                    "reasons_patient_leaves_home": ["string"],
                    "safety_measures": ["string"],
                    "supplemental_plan_of_treatment": ["string"],
                    "times_and_reasons_patient_not_at_home": ["string"],
                    "unusual_home_or_social_env": ["string"],
                    "updated_information": ["string"],
                },
                "claim_pricing_information": {
                    "pricing_methodology_code": "00",
                    "repriced_allowed_amount": "repricedAllowedAmount",
                    "exception_code": "1",
                    "policy_compliance_code": "1",
                    "product_or_service_id_qualifier": "ER",
                    "reject_reason_code": "T1",
                    "repriced_approved_amount": "repricedApprovedAmount",
                    "repriced_approved_drg_code": "repricedApprovedDRGCode",
                    "repriced_approved_hcpcs_code": "repricedApprovedHCPCSCode",
                    "repriced_approved_revenue_code": "repricedApprovedRevenueCode",
                    "repriced_approved_service_unit_code": "DA",
                    "repriced_approved_service_unit_count": "repricedApprovedServiceUnitCount",
                    "repriced_org_identifier": "repricedOrgIdentifier",
                    "repriced_per_diem": "repricedPerDiem",
                    "repriced_saving_amount": "repricedSavingAmount",
                },
                "claim_supplemental_information": {
                    "adjusted_repriced_claim_ref_number": "adjustedRepricedClaimRefNumber",
                    "auto_accident_state": "autoAccidentState",
                    "claim_control_number": "claimControlNumber",
                    "claim_number": "claimNumber",
                    "demo_project_identifier": "demoProjectIdentifier",
                    "investigational_device_exemption_number": "investigationalDeviceExemptionNumber",
                    "medical_record_number": "medicalRecordNumber",
                    "peer_review_authorization_number": "peerReviewAuthorizationNumber",
                    "prior_authorization_number": "priorAuthorizationNumber",
                    "referral_number": "referralNumber",
                    "report_information": {
                        "attachment_control_number": "xx",
                        "attachment_report_type_code": "03",
                        "attachment_transmission_code": "AA",
                    },
                    "report_informations": [
                        {
                            "attachment_control_number": "xx",
                            "attachment_report_type_code": "03",
                            "attachment_transmission_code": "AA",
                        }
                    ],
                    "repriced_claim_number": "repricedClaimNumber",
                    "service_authorization_exception_code": "1",
                },
                "condition_codes": ["AV"],
                "condition_codes_list": [[{"condition_code": "conditionCode"}]],
                "delay_reason_code": "1",
                "diagnosis_related_group_information": {"drug_related_group_code": "drugRelatedGroupCode"},
                "epsdt_referral": {
                    "certification_condition_code_applies_indicator": "N",
                    "condition_codes": ["AV"],
                },
                "external_cause_of_injuries": [
                    {
                        "external_cause_of_injury": "externalCauseOfInjury",
                        "qualifier_code": "ABN",
                        "present_on_admission_indicator": "N",
                    }
                ],
                "file_information": ["string"],
                "occurrence_information_list": [
                    [
                        {
                            "occurrence_span_code": "occurrenceSpanCode",
                            "occurrence_span_code_date": "73210630",
                        }
                    ]
                ],
                "occurrence_span_informations": [
                    [
                        {
                            "occurrence_span_code": "occurrenceSpanCode",
                            "occurrence_span_code_end_date": "73210630",
                            "occurrence_span_code_start_date": "73210630",
                        }
                    ]
                ],
                "other_diagnosis_information_list": [
                    [
                        {
                            "other_diagnosis_code": "otherDiagnosisCode",
                            "qualifier_code": "ABF",
                            "present_on_admission_indicator": "N",
                        }
                    ]
                ],
                "other_procedure_information_list": [
                    [
                        {
                            "other_procedure_code": "otherProcedureCode",
                            "qualifier_code": "BBQ",
                            "other_procedure_date": "73210630",
                        }
                    ]
                ],
                "other_subscriber_information": {
                    "benefits_assignment_certification_indicator": "N",
                    "claim_filing_indicator_code": "11",
                    "individual_relationship_code": "01",
                    "other_payer_name": {
                        "other_payer_identifier": "otherPayerIdentifier",
                        "other_payer_identifier_type_code": "PI",
                        "other_payer_organization_name": "otherPayerOrganizationName",
                        "other_insured_additional_identifier": "otherInsuredAdditionalIdentifier",
                        "other_payer_address": {
                            "address1": "address1",
                            "city": "city",
                            "address2": "address2",
                            "country_code": "xx",
                            "country_sub_division_code": "x",
                            "postal_code": "xxx",
                            "state": "xx",
                        },
                        "other_payer_adjudication_or_payment_date": "otherPayerAdjudicationOrPaymentDate",
                        "other_payer_claim_adjustment_indicator": True,
                        "other_payer_claim_control_number": "otherPayerClaimControlNumber",
                        "other_payer_prior_authorization_number": "otherPayerPriorAuthorizationNumber",
                        "other_payer_prior_authorization_or_referral_number": "otherPayerPriorAuthorizationOrReferralNumber",
                        "other_payer_secondary_identifier": [
                            {
                                "identifier": "identifier",
                                "qualifier": "qualifier",
                            }
                        ],
                    },
                    "other_subscriber_name": {
                        "other_insured_identifier": "otherInsuredIdentifier",
                        "other_insured_identifier_type_code": "II",
                        "other_insured_last_name": "otherInsuredLastName",
                        "other_insured_qualifier": "1",
                        "address": {
                            "address1": "address1",
                            "city": "city",
                            "address2": "address2",
                            "country_code": "xx",
                            "country_sub_division_code": "x",
                            "postal_code": "xxx",
                            "state": "xx",
                        },
                        "first_name": "firstName",
                        "other_insured_additional_identifier": ["string"],
                        "other_insured_first_name": "otherInsuredFirstName",
                        "other_insured_middle_name": "otherInsuredMiddleName",
                        "other_insured_suffix": "otherInsuredSuffix",
                    },
                    "payment_responsibility_level_code": "A",
                    "release_of_information_code": "I",
                    "claim_level_adjustments": [
                        {
                            "adjustment_group_code": "CO",
                            "claim_adjustment_details": [
                                {
                                    "adjustment_amount": "adjustmentAmount",
                                    "adjustment_reason_code": "adjustmentReasonCode",
                                    "adjustment_quantity": "adjustmentQuantity",
                                }
                            ],
                        }
                    ],
                    "group_number": "groupNumber",
                    "medicare_inpatient_adjudication": {
                        "covered_days_or_visits_count": "coveredDaysOrVisitsCount",
                        "capital_exception_amount": "capitalExceptionAmount",
                        "capital_hspdrg_amount": "capitalHSPDRGAmount",
                        "claim_disproportionate_share_amount": "claimDisproportionateShareAmount",
                        "claim_drg_amount": "claimDRGAmount",
                        "claim_indirect_teaching_amount": "claimIndirectTeachingAmount",
                        "claim_msp_pass_through_amount": "claimMspPassThroughAmount",
                        "claim_payment_remark_code": ["string"],
                        "claim_pps_capital_amount": "claimPpsCapitalAmount",
                        "claim_pps_capital_outlier_ammount": "claimPpsCapitalOutlierAmmount",
                        "cost_report_day_count": "costReportDayCount",
                        "lifetime_psychiatric_days_count": "lifetimePsychiatricDaysCount",
                        "non_payable_professional_component_billed_amount": "nonPayableProfessionalComponentBilledAmount",
                        "old_capital_amount": "oldCapitalAmount",
                        "pps_capital_dsh_drg_amount": "ppsCapitalDshDrgAmount",
                        "pps_capital_hsp_drg_amount": "ppsCapitalHspDrgAmount",
                        "pps_capital_ime_amount": "ppsCapitalImeAmount",
                        "pps_operating_federal_specific_drg_amount": "ppsOperatingFederalSpecificDrgAmount",
                        "pps_operating_hospital_specific_drg_amount": "ppsOperatingHospitalSpecificDrgAmount",
                    },
                    "medicare_outpatient_adjudication": {
                        "claim_payment_remark_code": ["string"],
                        "end_stage_renal_disease_payment_amount": "321669910225",
                        "hcpcs_payable_amount": "321669910225",
                        "non_payable_professional_component_billed_amount": "321669910225",
                        "reimbursement_rate": "reimbursementRate",
                    },
                    "non_covered_charge_amount": "nonCoveredChargeAmount",
                    "other_insured_group_name": "otherInsuredGroupName",
                    "other_payer_attending_provider": {
                        "other_payer_attending_provider_identifier": [
                            {
                                "identifier": "identifier",
                                "qualifier": "qualifier",
                            }
                        ]
                    },
                    "other_payer_billing_provider": {
                        "other_payer_billing_provider_identifier": [
                            {
                                "identifier": "identifier",
                                "qualifier": "qualifier",
                            }
                        ]
                    },
                    "other_payer_operating_physician": {
                        "other_payer_operating_physician_identifier": [
                            {
                                "identifier": "identifier",
                                "qualifier": "qualifier",
                            }
                        ]
                    },
                    "other_payer_other_operating_physician": {
                        "other_payer_other_operating_physician_identifier": [
                            {
                                "identifier": "identifier",
                                "qualifier": "qualifier",
                            }
                        ]
                    },
                    "other_payer_referring_provider": {
                        "other_payer_referring_provider_identifier": [
                            {
                                "identifier": "identifier",
                                "qualifier": "qualifier",
                            }
                        ]
                    },
                    "other_payer_rendering_provider": {
                        "other_payer_rendering_provider_identifier": [
                            {
                                "identifier": "identifier",
                                "qualifier": "qualifier",
                            }
                        ]
                    },
                    "other_payer_service_facility_location": {
                        "other_payer_service_facility_location_identifier": [
                            {
                                "identifier": "identifier",
                                "qualifier": "qualifier",
                            }
                        ]
                    },
                    "payer_paid_amount": "payerPaidAmount",
                    "policy_number": "policyNumber",
                    "remaining_patient_liability": "remainingPatientLiability",
                },
                "patient_amount_paid": "patientAmountPaid",
                "patient_estimated_amount_due": "321669910225",
                "patient_reason_for_visits": [
                    {
                        "patient_reason_for_visit_code": "patientReasonForVisitCode",
                        "qualifier_code": "APR",
                    }
                ],
                "patient_weight": "patientWeight",
                "principal_procedure_information": {
                    "principal_procedure_code": "principalProcedureCode",
                    "qualifier_code": "BBR",
                    "principal_procedure_date": "73210630",
                },
                "property_casualty_claim_number": "propertyCasualtyClaimNumber",
                "service_facility_location": {
                    "address": {
                        "address1": "address1",
                        "city": "city",
                        "address2": "address2",
                        "country_code": "xx",
                        "country_sub_division_code": "x",
                        "postal_code": "xxx",
                        "state": "xx",
                    },
                    "organization_name": "organizationName",
                    "identification_code": "identificationCode",
                    "secondary_identification_qualifier_code": "0B",
                    "secondary_identifier": "secondaryIdentifier",
                },
                "signature_indicator": "signatureIndicator",
                "treatment_code_information_list": [["string"]],
                "value_information_list": [
                    [
                        {
                            "value_code": "valueCode",
                            "value_code_amount": "321669910225",
                        }
                    ]
                ],
            },
            idempotency_key="idempotencyKey",
            is_testing=True,
            receiver={
                "organization_name": "organizationName",
                "tax_id": "xx",
            },
            submitter={
                "contact_information": {
                    "email": "email",
                    "fax_number": "faxNumber",
                    "name": "name",
                    "phone_number": "phoneNumber",
                    "valid_contact": True,
                },
                "organization_name": "organizationName",
                "tax_id": "xx",
            },
            subscriber={
                "first_name": "firstName",
                "last_name": "lastName",
                "payment_responsibility_level_code": "A",
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "xx",
                    "country_sub_division_code": "x",
                    "postal_code": "xxx",
                    "state": "xx",
                },
                "date_of_birth": "73210630",
                "gender": "M",
                "group_number": "groupNumber",
                "member_id": "xx",
                "middle_name": "middleName",
                "policy_number": "policyNumber",
                "ssn": "732166991",
                "standard_health_id": "standardHealthId",
                "suffix": "suffix",
            },
            trading_partner_service_id="tradingPartnerServiceId",
            attending={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "xx",
                    "country_sub_division_code": "x",
                    "postal_code": "xxx",
                    "state": "xx",
                },
                "contact_information": {
                    "name": "name",
                    "email": "email",
                    "fax_number": "faxNumber",
                    "phone_number": "phoneNumber",
                    "valid_contact": True,
                },
                "employer_id": "employerId",
                "first_name": "firstName",
                "last_name": "lastName",
                "middle_name": "middleName",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "provider_type": "providerType",
                "secondary_identification_qualifier_code": "0B",
                "secondary_identifier": "secondaryIdentifier",
                "suffix": "suffix",
                "taxonomy_code": "2E02VLfW09",
            },
            billing={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "xx",
                    "country_sub_division_code": "x",
                    "postal_code": "xxx",
                    "state": "xx",
                },
                "employer_id": "employerId",
                "npi": "7321669910",
                "commercial_number": "commercialNumber",
                "contact_information": {
                    "name": "name",
                    "email": "email",
                    "fax_number": "faxNumber",
                    "phone_number": "phoneNumber",
                    "valid_contact": True,
                },
                "first_name": "firstName",
                "last_name": "lastName",
                "location_number": "locationNumber",
                "middle_name": "middleName",
                "organization_name": "organizationName",
                "provider_type": "BillingProvider",
                "provider_upin_number": "providerUpinNumber",
                "secondary_identification_qualifier_code": "0B",
                "secondary_identifier": "secondaryIdentifier",
                "state_license_number": "stateLicenseNumber",
                "suffix": "suffix",
                "taxonomy_code": "2E02VLfW09",
            },
            billing_pay_to_address_name={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "xx",
                    "country_sub_division_code": "x",
                    "postal_code": "xxx",
                    "state": "xx",
                },
                "entity_type_qualifier": "2",
            },
            billing_pay_to_plan_name={
                "identification_code": "xx",
                "identification_code_qualifier": "PI",
                "organization_name": "organizationName",
                "tax_id": "732166991",
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "xx",
                    "country_sub_division_code": "x",
                    "postal_code": "xxx",
                    "state": "xx",
                },
                "claim_office_number": "claimOfficeNumber",
                "naic": "73216",
                "payer_identification_number": "payerIdentificationNumber",
            },
            control_number="155771193",
            correlation_id="correlationId",
            dependent={
                "date_of_birth": "73210630",
                "first_name": "firstName",
                "gender": "M",
                "last_name": "lastName",
                "relationship_to_subscriber_code": "01",
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "xx",
                    "country_sub_division_code": "x",
                    "postal_code": "xxx",
                    "state": "xx",
                },
                "middle_name": "middleName",
                "ssn": "732166991",
                "suffix": "suffix",
            },
            event_mapping={"received_277_ca": "RECEIVED_277CA"},
            operating_physician={
                "last_name": "lastName",
                "first_name": "firstName",
                "identification_qualifier_code": "0B",
                "middle_name": "middleName",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "secondary_identifier": "secondaryIdentifier",
                "suffix": "suffix",
            },
            other_operating_physician={
                "last_name": "lastName",
                "first_name": "firstName",
                "identification_qualifier_code": "0B",
                "middle_name": "middleName",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "secondary_identifier": "secondaryIdentifier",
                "suffix": "suffix",
            },
            payer_address={
                "address1": "address1",
                "city": "city",
                "address2": "address2",
                "country_code": "xx",
                "country_sub_division_code": "x",
                "postal_code": "xxx",
                "state": "xx",
            },
            providers=[
                {
                    "provider_type": "BillingProvider",
                    "address": {
                        "address1": "address1",
                        "city": "city",
                        "address2": "address2",
                        "country_code": "xx",
                        "country_sub_division_code": "x",
                        "postal_code": "xxx",
                        "state": "xx",
                    },
                    "contact_information": {
                        "name": "name",
                        "email": "email",
                        "fax_number": "faxNumber",
                        "phone_number": "phoneNumber",
                        "valid_contact": True,
                    },
                    "employer_id": "employerId",
                    "first_name": "firstName",
                    "last_name": "lastName",
                    "middle_name": "middleName",
                    "npi": "7321669910",
                    "organization_name": "organizationName",
                    "secondary_identification_qualifier_code": "0B",
                    "secondary_identifier": "secondaryIdentifier",
                    "suffix": "suffix",
                    "taxonomy_code": "2E02VLfW09",
                }
            ],
            referring={
                "last_name": "lastName",
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "xx",
                    "country_sub_division_code": "x",
                    "postal_code": "xxx",
                    "state": "xx",
                },
                "commercial_number": "commercialNumber",
                "contact_information": {
                    "name": "name",
                    "email": "email",
                    "fax_number": "faxNumber",
                    "phone_number": "phoneNumber",
                    "valid_contact": True,
                },
                "employer_id": "employerId",
                "first_name": "firstName",
                "location_number": "locationNumber",
                "middle_name": "middleName",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "provider_type": "ReferringProvider",
                "provider_upin_number": "providerUpinNumber",
                "secondary_identification_qualifier_code": "0B",
                "secondary_identifier": "secondaryIdentifier",
                "state_license_number": "stateLicenseNumber",
                "suffix": "suffix",
                "taxonomy_code": "2E02VLfW09",
            },
            rendering={
                "last_name": "lastName",
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "xx",
                    "country_sub_division_code": "x",
                    "postal_code": "xxx",
                    "state": "xx",
                },
                "commercial_number": "commercialNumber",
                "contact_information": {
                    "name": "name",
                    "email": "email",
                    "fax_number": "faxNumber",
                    "phone_number": "phoneNumber",
                    "valid_contact": True,
                },
                "employer_id": "employerId",
                "first_name": "firstName",
                "location_number": "locationNumber",
                "middle_name": "middleName",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "provider_type": "providerType",
                "provider_upin_number": "providerUpinNumber",
                "secondary_identification_qualifier_code": "0B",
                "secondary_identifier": "secondaryIdentifier",
                "state_license_number": "stateLicenseNumber",
                "suffix": "suffix",
                "taxonomy_code": "2E02VLfW09",
            },
            trading_partner_name="tradingPartnerName",
        )
        assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_submit(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.clearinghouse.claim.with_raw_response.submit(
            claim_information={
                "benefits_assignment_certification_indicator": "N",
                "claim_charge_amount": "321669910225",
                "claim_code_information": {
                    "admission_type_code": "x",
                    "patient_status_code": "x",
                },
                "claim_date_information": {
                    "statement_begin_date": "73210630",
                    "statement_end_date": "73210630",
                },
                "claim_filing_code": "11",
                "claim_frequency_code": "x",
                "place_of_service_code": "xx",
                "plan_participation_code": "A",
                "principal_diagnosis": {
                    "principal_diagnosis_code": "principalDiagnosisCode",
                    "qualifier_code": "ABK",
                },
                "release_information_code": "I",
                "service_lines": [
                    {
                        "institutional_service": {
                            "line_item_charge_amount": "321669910225",
                            "measurement_unit": "DA",
                            "service_line_revenue_code": "serviceLineRevenueCode",
                            "service_unit_count": "serviceUnitCount",
                        }
                    }
                ],
            },
            idempotency_key="idempotencyKey",
            is_testing=True,
            receiver={"organization_name": "organizationName"},
            submitter={
                "contact_information": {},
                "organization_name": "organizationName",
                "tax_id": "xx",
            },
            subscriber={
                "first_name": "firstName",
                "last_name": "lastName",
                "payment_responsibility_level_code": "A",
            },
            trading_partner_service_id="tradingPartnerServiceId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        claim = await response.parse()
        assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_submit(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.clearinghouse.claim.with_streaming_response.submit(
            claim_information={
                "benefits_assignment_certification_indicator": "N",
                "claim_charge_amount": "321669910225",
                "claim_code_information": {
                    "admission_type_code": "x",
                    "patient_status_code": "x",
                },
                "claim_date_information": {
                    "statement_begin_date": "73210630",
                    "statement_end_date": "73210630",
                },
                "claim_filing_code": "11",
                "claim_frequency_code": "x",
                "place_of_service_code": "xx",
                "plan_participation_code": "A",
                "principal_diagnosis": {
                    "principal_diagnosis_code": "principalDiagnosisCode",
                    "qualifier_code": "ABK",
                },
                "release_information_code": "I",
                "service_lines": [
                    {
                        "institutional_service": {
                            "line_item_charge_amount": "321669910225",
                            "measurement_unit": "DA",
                            "service_line_revenue_code": "serviceLineRevenueCode",
                            "service_unit_count": "serviceUnitCount",
                        }
                    }
                ],
            },
            idempotency_key="idempotencyKey",
            is_testing=True,
            receiver={"organization_name": "organizationName"},
            submitter={
                "contact_information": {},
                "organization_name": "organizationName",
                "tax_id": "xx",
            },
            subscriber={
                "first_name": "firstName",
                "last_name": "lastName",
                "payment_responsibility_level_code": "A",
            },
            trading_partner_service_id="tradingPartnerServiceId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            claim = await response.parse()
            assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

        assert cast(Any, response.is_closed) is True
