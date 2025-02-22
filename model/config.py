# One-hot encoding categories
ONE_HOT_COLUMNS = {
    'premium_payment_mode': ['Quarterly', 'Yearly', 'Half yearly', 'Monthly', 'Single'],
    'holder_marital_status': ['Single', 'Married', 'widowed', 'divorced'],
    'indiv_requirement_flag': ['Non Medical', 'Medical'],
    'product_type': ['ULIP', 'Traditional', 'Pension', 'Health', 'Non Par', 'Variable'],
    'channel': ['Retail Agency', 'Bancassurance', 'Institutional Alliance', 'Mail and Others'],
}

# Label encoding mappings
LABEL_ENCODINGS = {
    'nominee_relation': {
        'Brother': 0, 
        'Daughter': 1,
        'Father': 2, 
        'Grand Daughter': 3, 
        'Grand Son': 4,                 
        'Husband': 5, 
        'Mother': 6, 
        'Nephew': 7, 
        'Niece': 8, 
        'Sister': 9, 
        'Son': 10,
        'Spouse': 11, 
        'Wife': 12
    },
    'status':{
        'Cancellation': 0, 
        'Claim': 1, 
        'Inforce': 2, 
        'Lapse': 3, 
        'Maturity': 4, 
        'Rejection': 5, 
        'Technical Lapse': 6, 
        'Terminated': 7, 
        'Withdrawal': 8
    },
    'sub_status':{
        ' ': 0,
        '-': 1, 
        'Death Claim Paid': 2, 
        'Death Claim Repudiated': 3, 
        'Declined': 4, 
        'Dishonour': 5, 
        'Disinvested Paid': 6, 
        'Disinvested Unpaid': 7, 
        'Free Look Cancellation': 8, 
        'Intimated Death Claim': 9, 
        'Intimated Death Claim-Annuity': 10, 
        'Other Reason': 11, 
        'Paid Up': 12, 
        'Refunded': 13, 
        'Surrendered': 14, 
        'Surrendered Reinvested Auto': 15, 
        'Unpaid': 16
    },
    'occupation': {
        'Agriculturist': 0, 
        'Army': 1, 
        'Business': 2, 
        'Construction Labour': 3,
        'Defense Retired': 4, 
        'Family Pension': 5, 
        'Housewife': 6, 
        'Other Arm Forces Except Police': 7,
        'Profession': 8, 
        'Retired': 9, 
        'Self-Employed': 10, 
        'Service': 11, 
        'Student': 12
    }
}

FRAUD_CATEGORY = {
    0: 'Agent Dual Pan Card',
    1: 'Claims Fraud',
    2: 'Document Tampering',
    3: 'Impersonation',
    4: 'Kickback',
    5: 'Logging in business not sourced by oneself',
    6: 'Misappropriating Funds',
    7: 'Misappropriating funds',
    8: 'Misrepresentation',
    9: 'Misselling ',
    10: 'Signature Forgery',
    11: 'Unauthorized activity'
}    


# Mean and standard deviation for numerical features
MEAN_STD = {
    'assured_age': (46.88, 10.53),
    'policy_sum_assured': (1090620.55, 1976036.62),
    'premium': (190290.47, 441873.88),
    'annual_income': (2259169.14, 29279866.28)
}

# Min and max values for numerical features
MIN_MAX = {
    'policy_term': (5.0, 80.0),
    'policy_payment_term': (3.0, 10.0),
    'policy_to_death_days': (-31.0, 1026.0),
    'death_to_intimation_days': (-1.0, 420.0),
    'policy_to_intimation_days': (-1.0, 1244.0)
}
