import mysql.connector

import os

# Database Configuration (using environment variables)
# Defaults set to TiDB Cloud
db_config = {
    'host': os.getenv('DB_HOST', 'gateway01.ap-southeast-1.prod.aws.tidbcloud.com'),
    'user': os.getenv('DB_USER', '4ZdPwsvVAA22Zwg.root'),
    'password': os.getenv('DB_PASSWORD', 'PpzUNJyDdDhBE0z8'),
    'database': os.getenv('DB_NAME', 'test'),
    'port': int(os.getenv('DB_PORT', 4000)),
    'ssl_verify_cert': True,
    'ssl_verify_identity': True
}

schemes_data = [
    # ---- 10 FARMER SCHEMES ----
    {
        'name': 'PM-KISAN Samman Nidhi',
        'description': 'Under this scheme, an income support of Rs. 6,000/- per year in three equal installments will be provided to all landholding farmer families.',
        'link': 'https://pmkisan.gov.in/',
        'domain_name': 'pmkisan.gov.in',
        'scheme_type': 'Central Sector Scheme',
        'age_requirement': 18,
        'min_annual_income': 0, # No specific limit, based on landholding
        'caste_requirement': 'No Requirement',
        'categories': 'Farmer'
    },
    {
        'name': 'Pradhan Mantri Fasal Bima Yojana (PMFBY)',
        'description': 'Provides insurance coverage and financial support to the farmers in the event of failure of any of the notified crops as a result of natural calamities.',
        'link': 'https://pmfby.gov.in/',
        'domain_name': 'pmfby.gov.in',
        'scheme_type': 'Crop Insurance',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Farmer'
    },
    {
        'name': 'Kisan Credit Card (KCC)',
        'description': 'Meets the comprehensive credit requirements of the agriculture sector and farmers for fisheries and animal husbandry by giving financial support.',
        'link': 'https://sbi.co.in/web/agri-rural/agriculture-banking/crop-loan/kisan-credit-card',
        'domain_name': 'sbi.co.in',
        'scheme_type': 'Financial Support',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Farmer,Business'
    },
    {
        'name': 'National Agriculture Market (e-NAM)',
        'description': 'A pan-India electronic trading portal which networks the existing APMC mandis to create a unified national market for agricultural commodities.',
        'link': 'https://enam.gov.in/',
        'domain_name': 'enam.gov.in',
        'scheme_type': 'Agricultural Trading',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Farmer,Business'
    },
    {
        'name': 'Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)',
        'description': 'Formulated with the vision of extending the coverage of irrigation and improving water use efficiency in a focused manner.',
        'link': 'https://pmksy.gov.in/',
        'domain_name': 'pmksy.gov.in',
        'scheme_type': 'Irrigation',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Farmer'
    },
    {
        'name': 'Paramparagat Krishi Vikas Yojana (PKVY)',
        'description': 'Promotes commercial organic farming through cluster approach and Participatory Guarantee System (PGS) certification.',
        'link': 'https://pgsindia-ncof.gov.in/pkvy/index.aspx',
        'domain_name': 'pgsindia-ncof.gov.in',
        'scheme_type': 'Organic Farming',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Farmer'
    },
    {
        'name': 'Soil Health Card Scheme',
        'description': 'Aims at promoting soil test based and balanced use of fertilizers to enable farmers to realize higher yields at lower cost.',
        'link': 'https://soilhealth.dac.gov.in/',
        'domain_name': 'soilhealth.dac.gov.in',
        'scheme_type': 'Agricultural Support',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Farmer'
    },
    {
        'name': 'Agriculture Infrastructure Fund',
        'description': 'Medium - long term debt financing facility for investment in viable projects for post-harvest management Infrastructure.',
        'link': 'https://agriinfra.dac.gov.in/',
        'domain_name': 'agriinfra.dac.gov.in',
        'scheme_type': 'Infrastructure Finance',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Farmer,Business'
    },
    {
        'name': 'Rashtriya Krishi Vikas Yojana (RKVY)',
        'description': 'Incentivizes States to increase public investment in Agriculture & allied sectors to promote broad-based agricultural growth.',
        'link': 'https://rkvy.nic.in/',
        'domain_name': 'rkvy.nic.in',
        'scheme_type': 'State Incentive',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Farmer'
    },
    {
        'name': 'Rythu Bandhu Scheme (Telangana)',
        'description': 'Provides investment support for agriculture and horticulture crops by way of grant of Rs. 5,000 per acre per season.',
        'link': 'https://rythubandhu.telangana.gov.in/',
        'domain_name': 'rythubandhu.telangana.gov.in',
        'scheme_type': 'State Level Support',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Farmer'
    },

    # ---- 10 STUDENT SCHEMES ----
    {
        'name': 'National Means-cum-Merit Scholarship (NMMS)',
        'description': 'Provides financial assistance to meritorious students of economically weaker sections to arrest their drop out at class VIII.',
        'link': 'https://scholarships.gov.in/',
        'domain_name': 'scholarships.gov.in',
        'scheme_type': 'Scholarship',
        'age_requirement': 13,
        'min_annual_income': 350000,
        'caste_requirement': 'No Requirement',
        'categories': 'Student'
    },
    {
        'name': 'Post Matric Scholarship for SC/ST/OBC',
        'description': 'Provides financial assistance to SC/ST/OBC students studying at post matriculation or post-secondary stage to complete their education.',
        'link': 'https://scholarships.gov.in/',
        'domain_name': 'scholarships.gov.in',
        'scheme_type': 'Category Specific Scholarship',
        'age_requirement': 16,
        'min_annual_income': 250000,
        'caste_requirement': 'SC, ST, OBC',
        'categories': 'Student'
    },
    {
        'name': 'Pradhan Mantri Vidyalakshmi Karyakram',
        'description': 'A portal for students seeking Education Loan to view, apply and track the education loan applications to banks anytime, anywhere.',
        'link': 'https://www.vidyalakshmi.co.in/',
        'domain_name': 'vidyalakshmi.co.in',
        'scheme_type': 'Education Loan',
        'age_requirement': 16,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Student'
    },
    {
        'name': 'AICTE Pragati Scholarship for Girls',
        'description': 'Assistance to girls pursuing technical education to ensure that women are given an opportunity to participate in the nation\'s development.',
        'link': 'https://www.aicte-india.org/schemes/students-development-schemes',
        'domain_name': 'aicte-india.org',
        'scheme_type': 'Women Scholarship',
        'age_requirement': 16,
        'min_annual_income': 800000,
        'caste_requirement': 'No Requirement',
        'categories': 'Student'
    },
    {
        'name': 'Inspire Scholarship',
        'description': 'Innovation in Science Pursuit for Inspired Research offers financial rewards to attract talent to science studying subjects like Basic and Natural Sciences.',
        'link': 'https://online-inspire.gov.in/',
        'domain_name': 'online-inspire.gov.in',
        'scheme_type': 'Science Fellowship',
        'age_requirement': 17,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Student'
    },
    {
        'name': 'Kishore Vaigyanik Protsahan Yojana (KVPY)',
        'description': 'National Program of Fellowship in Basic Sciences, initiated and funded by the Department of Science and Technology.',
        'link': 'http://kvpy.iisc.ac.in/',
        'domain_name': 'kvpy.iisc.ac.in',
        'scheme_type': 'Fellowship',
        'age_requirement': 16,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Student'
    },
    {
        'name': 'Begum Hazrat Mahal National Scholarship',
        'description': 'Merit-cum-means scholarship for meritorious girl students belonging to minority communities.',
        'link': 'https://scholarships.gov.in/',
        'domain_name': 'scholarships.gov.in',
        'scheme_type': 'Minority Girls Scholarship',
        'age_requirement': 14,
        'min_annual_income': 200000,
        'caste_requirement': 'Minority',
        'categories': 'Student'
    },
    {
        'name': 'Prime Minister\'s Special Scholarship Scheme (PMSSS) for J&K',
        'description': 'Equips the youth of J&K with knowledge, skills, and experience to secure employment globally.',
        'link': 'https://www.aicte-india.org/bureaus/jk',
        'domain_name': 'aicte-india.org',
        'scheme_type': 'Regional Education',
        'age_requirement': 17,
        'min_annual_income': 800000,
        'caste_requirement': 'No Requirement',
        'categories': 'Student'
    },
    {
        'name': 'Swami Vivekananda Merit Cum Means Scholarship',
        'description': 'Assists meritorious students belonging to economically backward families to pursue higher studies in West Bengal.',
        'link': 'https://svmcm.wbhed.gov.in/',
        'domain_name': 'svmcm.wbhed.gov.in',
        'scheme_type': 'State Based Scholarship',
        'age_requirement': 16,
        'min_annual_income': 250000,
        'caste_requirement': 'No Requirement',
        'categories': 'Student'
    },
    {
        'name': 'Central Sector Scheme of Scholarship for College and University Students',
        'description': 'Provides financial assistance to meritorious students from low income families to meet day-to-day expenses while pursuing higher studies.',
        'link': 'https://scholarships.gov.in/',
        'domain_name': 'scholarships.gov.in',
        'scheme_type': 'Merit Scholarship',
        'age_requirement': 17,
        'min_annual_income': 800000,
        'caste_requirement': 'No Requirement',
        'categories': 'Student'
    },

    # ---- 10 UNEMPLOYED SCHEMES ----
    {
        'name': 'Prime Minister\'s Employment Generation Programme (PMEGP)',
        'description': 'Credit-linked subsidy programme to generate employment opportunities through establishment of micro-enterprises in rural and urban areas.',
        'link': 'https://www.kviconline.gov.in/pmegpeportal/pmegphome/index.jsp',
        'domain_name': 'kviconline.gov.in',
        'scheme_type': 'Employment Generation',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Unemployed,Business'
    },
    {
        'name': 'Deen Dayal Upadhyaya Grameen Kaushalya Yojana (DDU-GKY)',
        'description': 'DDU-GKY aims to skill rural youth who are poor and provide them with jobs having regular monthly wages or above the minimum wages.',
        'link': 'http://ddugky.gov.in/',
        'domain_name': 'ddugky.gov.in',
        'scheme_type': 'Skill Development',
        'age_requirement': 15,
        'min_annual_income': 200000,
        'caste_requirement': 'No Requirement',
        'categories': 'Unemployed,Student'
    },
    {
        'name': 'Pradhan Mantri Kaushal Vikas Yojana (PMKVY)',
        'description': 'Flagship scheme of the Ministry of Skill Development to enable Indian youth to take up industry-relevant skill training that will help them in securing a better livelihood.',
        'link': 'https://www.pmkvyofficial.org/',
        'domain_name': 'pmkvyofficial.org',
        'scheme_type': 'Skill Training',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Unemployed'
    },
    {
        'name': 'Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA)',
        'description': 'Provides at least 100 days of guaranteed wage employment in a financial year to every rural household whose adult members volunteer to do unskilled manual work.',
        'link': 'https://nrega.nic.in/',
        'domain_name': 'nrega.nic.in',
        'scheme_type': 'Rural Employment guarantee',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Unemployed,Farmer'
    },
    {
        'name': 'Atmanirbhar Bharat Rojgar Yojana (ABRY)',
        'description': 'Incentivizes employers for creation of new employment along with social security benefits and restoration of loss of employment during COVID-19 pandemic.',
        'link': 'https://www.epfindia.gov.in/',
        'domain_name': 'epfindia.gov.in',
        'scheme_type': 'Employment Subsidy',
        'age_requirement': 18,
        'min_annual_income': 180000,
        'caste_requirement': 'No Requirement',
        'categories': 'Unemployed,Business'
    },
    {
        'name': 'Pradhan Mantri Rojgar Protsahan Yojana (PMRPY)',
        'description': 'Designed to incentivize employers for generation of new employment by paying the 8.33% EPS contribution of the employer for the new employees.',
        'link': 'https://pmrpy.gov.in/',
        'domain_name': 'pmrpy.gov.in',
        'scheme_type': 'Employer Incentive',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Unemployed,Business'
    },
    {
        'name': 'National Career Service (NCS)',
        'description': 'A portal linking job-seekers to employers offering various services like career counseling, job matching, and vocational guidance.',
        'link': 'https://www.ncs.gov.in/',
        'domain_name': 'ncs.gov.in',
        'scheme_type': 'Employment Portal',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Unemployed'
    },
    {
        'name': 'State Unemployment Allowance Scheme',
        'description': 'Provides a monthly allowance to educated unemployed youth registered with employment exchanges (Varies by State).',
        'link': 'https://www.ncs.gov.in/', # Placeholder, highly state dependent
        'domain_name': 'ncs.gov.in',
        'scheme_type': 'Financial Allowance',
        'age_requirement': 21,
        'min_annual_income': 200000,
        'caste_requirement': 'No Requirement',
        'categories': 'Unemployed'
    },
    {
        'name': 'Mukhyamantri Yuva Swarozgar Yojana',
        'description': 'Provides financial aid and margin money subsidy for establishing small enterprises in unserved areas by educated unemployed youth.',
        'link': 'https://msme.up.gov.in/', # Example UP portal
        'domain_name': 'msme.up.gov.in',
        'scheme_type': 'Self Employment',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Unemployed,Business'
    },
    {
        'name': 'Skill India Digital Hub (SID)',
        'description': 'A unified platform providing access to integrated skilling, education, and employment ecosystem to build a future-ready workforce.',
        'link': 'https://www.skillindiadigital.gov.in/',
        'domain_name': 'skillindiadigital.gov.in',
        'scheme_type': 'Skilling Portal',
        'age_requirement': 16,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Unemployed,Student'
    },

    # ---- 10 BUSINESS SCHEMES ----
    {
        'name': 'Pradhan Mantri Mudra Yojana (PMMY)',
        'description': 'Provides loans up to 10 lakhs to non-corporate, non-farm small/micro enterprises classified under Shishu, Kishore, and Tarun categories.',
        'link': 'https://www.mudra.org.in/',
        'domain_name': 'mudra.org.in',
        'scheme_type': 'Microfinance Loan',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Business,Unemployed'
    },
    {
        'name': 'Stand Up India Scheme',
        'description': 'Facilitates bank loans between 10 lakh and 1 Crore to at least one SC or ST borrower and one woman borrower per bank branch for setting up a greenfield enterprise.',
        'link': 'https://www.standupmitra.in/',
        'domain_name': 'standupmitra.in',
        'scheme_type': 'SC/ST/Women Entrepreneurship',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'SC, ST',
        'categories': 'Business'
    },
    {
        'name': 'Startup India Seed Fund Scheme (SISFS)',
        'description': 'Provides financial assistance to startups for proof of concept, prototype development, product trials, market entry, and commercialization.',
        'link': 'https://seedfund.startupindia.gov.in/',
        'domain_name': 'startupindia.gov.in',
        'scheme_type': 'Startup Funding',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Business'
    },
    {
        'name': 'Credit Guarantee Fund Trust for Micro and Small Enterprises (CGTMSE)',
        'description': 'Facilitates collateral-free credit to the micro and small enterprise sector to encourage entrepreneurship and generate employment.',
        'link': 'https://www.cgtmse.in/',
        'domain_name': 'cgtmse.in',
        'scheme_type': 'Loan Guarantee',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Business'
    },
    {
        'name': 'MSME Market Development Assistance (MDA)',
        'description': 'Encourages Small & Micro manufacturing enterprises to tap and develop overseas markets through participation in international exhibitions/trade fairs.',
        'link': 'https://msme.gov.in/market-development-assistance-mda',
        'domain_name': 'msme.gov.in',
        'scheme_type': 'Export Promotion',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Business'
    },
    {
        'name': 'ZED Certification Scheme',
        'description': 'Aim to promote Zero Defect and Zero Effect practices among MSMEs to enhance quality and environmental sustainability.',
        'link': 'https://zed.msme.gov.in/',
        'domain_name': 'zed.msme.gov.in',
        'scheme_type': 'Quality Certification',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Business'
    },
    {
        'name': 'ASPIRE (A Scheme for Promotion of Innovation, Rural Industries and Entrepreneurship)',
        'description': 'Aims to set up a network of technology centers and incubation centers to accelerate entrepreneurship and also to promote startups for innovation in agro-industry.',
        'link': 'https://aspire.msme.gov.in/',
        'domain_name': 'aspire.msme.gov.in',
        'scheme_type': 'Agro Innovation',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Business'
    },
    {
        'name': 'Coir Vikas Yojana',
        'description': 'Supports the coir industry through skill upgradation, development of new machinery, and financial assistance for modernizing coir units.',
        'link': 'http://coirboard.gov.in/',
        'domain_name': 'coirboard.gov.in',
        'scheme_type': 'Sector Specific Support',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Business'
    },
    {
        'name': 'National SC-ST Hub',
        'description': 'Provides professional support to Scheduled Caste and Scheduled Tribe entrepreneurs to fulfil the obligations under the Central Government Public Procurement Policy.',
        'link': 'https://www.scsthub.in/',
        'domain_name': 'scsthub.in',
        'scheme_type': 'SC/ST Entrepreneurship',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'SC, ST',
        'categories': 'Business'
    },
    {
        'name': 'Trade Related Entrepreneurship Assistance and Development (TREAD) Scheme for Women',
        'description': 'Economic empowerment of women through the development of their entrepreneurial skills in non-farm activities.',
        'link': 'https://msme.gov.in/',
        'domain_name': 'msme.gov.in',
        'scheme_type': 'Women Entrepreneurship',
        'age_requirement': 18,
        'min_annual_income': 0,
        'caste_requirement': 'No Requirement',
        'categories': 'Business'
    }
]

def seed_db():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Clear existing schemes
        cursor.execute("TRUNCATE TABLE schemes")
        
        insert_query = """
        INSERT INTO schemes (name, description, link, domain_name, scheme_type, age_requirement, min_annual_income, caste_requirement, categories)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for scheme in schemes_data:
            cursor.execute(insert_query, (
                scheme['name'],
                scheme['description'],
                scheme['link'],
                scheme['domain_name'],
                scheme['scheme_type'],
                scheme['age_requirement'],
                scheme['min_annual_income'],
                scheme['caste_requirement'],
                scheme['categories']
            ))

        conn.commit()
        print(f"Successfully seeded {len(schemes_data)} schemes into the database.")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    seed_db()
