from datetime import date
from sqlalchemy.orm import Session

# Assuming your backend structure
from backend.database import SessionLocal, initialize_schema
from backend.models import Bursary, Institution, Programme

from backend.seed_data.private_data import private_data
from backend.seed_data.tvet_data import tvet_data
from backend.seed_data.university_data import university_data

def seed_institutions(session: Session):
    """
    Idempotent seeding of Institutions.
    Checks if an institution with the same name exists before inserting.
    """
    institutions_data = [
        # --- 26 Public Universities ---
        {"name": "University of Cape Town", "short_name": "UCT", "type": "University", "province": "Western Cape"},
        {"name": "Stellenbosch University", "short_name": "SU", "type": "University", "province": "Western Cape"},
        {"name": "University of the Western Cape", "short_name": "UWC", "type": "University", "province": "Western Cape"},
        {"name": "Cape Peninsula University of Technology", "short_name": "CPUT", "type": "University", "province": "Western Cape"},
        {"name": "University of the Witwatersrand", "short_name": "Wits", "type": "University", "province": "Gauteng"},
        {"name": "University of Pretoria", "short_name": "UP", "type": "University", "province": "Gauteng"},
        {"name": "University of Johannesburg", "short_name": "UJ", "type": "University", "province": "Gauteng"},
        {"name": "Tshwane University of Technology", "short_name": "TUT", "type": "University", "province": "Gauteng"},
        {"name": "Vaal University of Technology", "short_name": "VUT", "type": "University", "province": "Gauteng"},
        {"name": "Sefako Makgatho Health Sciences University", "short_name": "SMU", "type": "University", "province": "Gauteng"},
        {"name": "University of South Africa", "short_name": "UNISA", "type": "University", "province": "Gauteng"},
        {"name": "University of KwaZulu-Natal", "short_name": "UKZN", "type": "University", "province": "KwaZulu-Natal"},
        {"name": "Durban University of Technology", "short_name": "DUT", "type": "University", "province": "KwaZulu-Natal"},
        {"name": "Mangosuthu University of Technology", "short_name": "MUT", "type": "University", "province": "KwaZulu-Natal"},
        {"name": "University of Zululand", "short_name": "UniZulu", "type": "University", "province": "KwaZulu-Natal"},
        {"name": "University of Fort Hare", "short_name": "UFH", "type": "University", "province": "Eastern Cape"},
        {"name": "Nelson Mandela University", "short_name": "NMU", "type": "University", "province": "Eastern Cape"},
        {"name": "Rhodes University", "short_name": "RU", "type": "University", "province": "Eastern Cape"},
        {"name": "Walter Sisulu University", "short_name": "WSU", "type": "University", "province": "Eastern Cape"},
        {"name": "University of the Free State", "short_name": "UFS", "type": "University", "province": "Free State"},
        {"name": "Central University of Technology", "short_name": "CUT", "type": "University", "province": "Free State"},
        {"name": "University of Limpopo", "short_name": "UL", "type": "University", "province": "Limpopo"},
        {"name": "University of Venda", "short_name": "UNIVEN", "type": "University", "province": "Limpopo"},
        {"name": "University of Mpumalanga", "short_name": "UMP", "type": "University", "province": "Mpumalanga"},
        {"name": "North-West University", "short_name": "NWU", "type": "University", "province": "North West"},
        {"name": "Sol Plaatje University", "short_name": "SPU", "type": "University", "province": "Northern Cape"},

        # --- 50 Public TVET Colleges ---
        {"name": "Central Johannesburg TVET College", "short_name": "CJC", "type": "TVET", "province": "Gauteng"},
        {"name": "Ekurhuleni East TVET College", "short_name": "EEC", "type": "TVET", "province": "Gauteng"},
        {"name": "Ekurhuleni West TVET College", "short_name": "EWC", "type": "TVET", "province": "Gauteng"},
        {"name": "Sedibeng TVET College", "short_name": "Sedibeng", "type": "TVET", "province": "Gauteng"},
        {"name": "South West Gauteng TVET College", "short_name": "SWGC", "type": "TVET", "province": "Gauteng"},
        {"name": "Tshwane North TVET College", "short_name": "TNC", "type": "TVET", "province": "Gauteng"},
        {"name": "Tshwane South TVET College", "short_name": "TSC", "type": "TVET", "province": "Gauteng"},
        {"name": "Western TVET College", "short_name": "WTC", "type": "TVET", "province": "Gauteng"},
        {"name": "Boland TVET College", "short_name": "Boland", "type": "TVET", "province": "Western Cape"},
        {"name": "College of Cape Town for TVET", "short_name": "CCT", "type": "TVET", "province": "Western Cape"},
        {"name": "False Bay TVET College", "short_name": "False Bay", "type": "TVET", "province": "Western Cape"},
        {"name": "Northlink TVET College", "short_name": "Northlink", "type": "TVET", "province": "Western Cape"},
        {"name": "South Cape TVET College", "short_name": "South Cape", "type": "TVET", "province": "Western Cape"},
        {"name": "West Coast TVET College", "short_name": "West Coast", "type": "TVET", "province": "Western Cape"},
        {"name": "Coastal KZN TVET College", "short_name": "Coastal KZN", "type": "TVET", "province": "KwaZulu-Natal"},
        {"name": "Elangeni TVET College", "short_name": "Elangeni", "type": "TVET", "province": "KwaZulu-Natal"},
        {"name": "Esayidi TVET College", "short_name": "Esayidi", "type": "TVET", "province": "KwaZulu-Natal"},
        {"name": "Majuba TVET College", "short_name": "Majuba", "type": "TVET", "province": "KwaZulu-Natal"},
        {"name": "Mnambithi TVET College", "short_name": "Mnambithi", "type": "TVET", "province": "KwaZulu-Natal"},
        {"name": "Mthashana TVET College", "short_name": "Mthashana", "type": "TVET", "province": "KwaZulu-Natal"},
        {"name": "Thekwini TVET College", "short_name": "Thekwini", "type": "TVET", "province": "KwaZulu-Natal"},
        {"name": "Umfolozi TVET College", "short_name": "Umfolozi", "type": "TVET", "province": "KwaZulu-Natal"},
        {"name": "Umgungundlovu TVET College", "short_name": "Umgungundlovu", "type": "TVET", "province": "KwaZulu-Natal"},
        {"name": "Buffalo City TVET College", "short_name": "Buffalo City", "type": "TVET", "province": "Eastern Cape"},
        {"name": "Eastcape Midlands TVET College", "short_name": "EMC", "type": "TVET", "province": "Eastern Cape"},
        {"name": "Ikhala TVET College", "short_name": "Ikhala", "type": "TVET", "province": "Eastern Cape"},
        {"name": "Ingwe TVET College", "short_name": "Ingwe", "type": "TVET", "province": "Eastern Cape"},
        {"name": "King Hintsa TVET College", "short_name": "King Hintsa", "type": "TVET", "province": "Eastern Cape"},
        {"name": "King Sabata Dalindyebo TVET College", "short_name": "KSD", "type": "TVET", "province": "Eastern Cape"},
        {"name": "Lovedale TVET College", "short_name": "Lovedale", "type": "TVET", "province": "Eastern Cape"},
        {"name": "Port Elizabeth TVET College", "short_name": "PE College", "type": "TVET", "province": "Eastern Cape"},
        {"name": "Capricorn TVET College", "short_name": "Capricorn", "type": "TVET", "province": "Limpopo"},
        {"name": "Lephalale TVET College", "short_name": "Lephalale", "type": "TVET", "province": "Limpopo"},
        {"name": "Letaba TVET College", "short_name": "Letaba", "type": "TVET", "province": "Limpopo"},
        {"name": "Mopani South East TVET College", "short_name": "Mopani", "type": "TVET", "province": "Limpopo"},
        {"name": "Sekhukhune TVET College", "short_name": "Sekhukhune", "type": "TVET", "province": "Limpopo"},
        {"name": "Vhembe TVET College", "short_name": "Vhembe", "type": "TVET", "province": "Limpopo"},
        {"name": "Waterberg TVET College", "short_name": "Waterberg", "type": "TVET", "province": "Limpopo"},
        {"name": "Flavius Mareka TVET College", "short_name": "Flavius Mareka", "type": "TVET", "province": "Free State"},
        {"name": "Goldfields TVET College", "short_name": "Goldfields", "type": "TVET", "province": "Free State"},
        {"name": "Maluti TVET College", "short_name": "Maluti", "type": "TVET", "province": "Free State"},
        {"name": "Motheo TVET College", "short_name": "Motheo", "type": "TVET", "province": "Free State"},
        {"name": "Ehlanzeni TVET College", "short_name": "Ehlanzeni", "type": "TVET", "province": "Mpumalanga"},
        {"name": "Gert Sibande TVET College", "short_name": "Gert Sibande", "type": "TVET", "province": "Mpumalanga"},
        {"name": "Nkangala TVET College", "short_name": "Nkangala", "type": "TVET", "province": "Mpumalanga"},
        {"name": "Orbit TVET College", "short_name": "Orbit", "type": "TVET", "province": "North West"},
        {"name": "Taletso TVET College", "short_name": "Taletso", "type": "TVET", "province": "North West"},
        {"name": "Vuselela TVET College", "short_name": "Vuselela", "type": "TVET", "province": "North West"},
        {"name": "Northern Cape Rural TVET College", "short_name": "NCR", "type": "TVET", "province": "Northern Cape"},
        {"name": "Northern Cape Urban TVET College", "short_name": "NCU", "type": "TVET", "province": "Northern Cape"},

        # --- 80+ Private Higher Education Institutions ---
        {"name": "AAA School of Advertising", "short_name": "AAA", "type": "Private", "province": "Gauteng"},
        {"name": "Academy for Facilities Management", "short_name": "A4FM", "type": "Private", "province": "Gauteng"},
        {"name": "Academy of Sound Engineering", "short_name": "ASE", "type": "Private", "province": "Western Cape"},
        {"name": "ACT Cape Town", "short_name": "ACT", "type": "Private", "province": "Western Cape"},
        {"name": "Afrikaanse Protestantse Akademie", "short_name": "APA", "type": "Private", "province": "Gauteng"},
        {"name": "Akademia NPC", "short_name": "Akademia", "type": "Private", "province": "Gauteng"},
        {"name": "Akademiese Reformatoriese Opleiding en Studies", "short_name": "AROS", "type": "Private", "province": "Gauteng"},
        {"name": "Animation School", "short_name": "Animation", "type": "Private", "province": "Western Cape"},
        {"name": "Baptist Theological College of Southern Africa", "short_name": "BTC", "type": "Private", "province": "Gauteng"},
        {"name": "Belgium Campus iTversity", "short_name": "Belgium Campus", "type": "Private", "province": "Gauteng"},
        {"name": "Berea College of Technology", "short_name": "Berea", "type": "Private", "province": "KwaZulu-Natal"},
        {"name": "BHC School of Design", "short_name": "BHC", "type": "Private", "province": "Western Cape"},
        {"name": "Boston City Campus", "short_name": "Boston", "type": "Private", "province": "Gauteng"},
        {"name": "Boston Media House", "short_name": "BMH", "type": "Private", "province": "Gauteng"},
        {"name": "Business Management Training College", "short_name": "BMTC", "type": "Private", "province": "Gauteng"},
        {"name": "Cape Audio College", "short_name": "CAC", "type": "Private", "province": "Western Cape"},
        {"name": "Cape Town Baptist Seminary", "short_name": "CTBS", "type": "Private", "province": "Western Cape"},
        {"name": "Cape Town College of Fashion Design", "short_name": "CTCFD", "type": "Private", "province": "Western Cape"},
        {"name": "Cape Town Creative Academy", "short_name": "CTCA", "type": "Private", "province": "Western Cape"},
        {"name": "Centre for Creative Education", "short_name": "CCE", "type": "Private", "province": "Western Cape"},
        {"name": "Christ Baptist Church Seminary", "short_name": "CBCS", "type": "Private", "province": "Gauteng"},
        {"name": "Christian Reformed Theological Seminary", "short_name": "CRTS", "type": "Private", "province": "Gauteng"},
        {"name": "College of Transfiguration", "short_name": "COT", "type": "Private", "province": "Eastern Cape"},
        {"name": "Cornerstone Institute", "short_name": "Cornerstone", "type": "Private", "province": "Western Cape"},
        {"name": "Cranefield College", "short_name": "Cranefield", "type": "Private", "province": "Gauteng"},
        {"name": "Da Vinci Institute for Technology Management", "short_name": "Da Vinci", "type": "Private", "province": "Gauteng"},
        {"name": "Design Academy of Fashion", "short_name": "DAF", "type": "Private", "province": "Western Cape"},
        {"name": "Edutel Higher Education", "short_name": "Edutel", "type": "Private", "province": "Gauteng"},
        {"name": "Eduvos", "short_name": "Eduvos", "type": "Private", "province": "Gauteng"},
        {"name": "Elizabeth Galloway Academy of Fashion Design", "short_name": "EGAFD", "type": "Private", "province": "Western Cape"},
        {"name": "Empilweni Education", "short_name": "Empilweni", "type": "Private", "province": "Gauteng"},
        {"name": "ESRI South Africa", "short_name": "ESRI", "type": "Private", "province": "Gauteng"},
        {"name": "Exercise Teachers Academy", "short_name": "ETA", "type": "Private", "province": "Western Cape"},
        {"name": "FEDISA", "short_name": "FEDISA", "type": "Private", "province": "Western Cape"},
        {"name": "Friends of Design – Academy of Digital Arts", "short_name": "FoD", "type": "Private", "province": "Western Cape"},
        {"name": "Foundation for Professional Development", "short_name": "FPD", "type": "Private", "province": "Gauteng"},
        {"name": "George Whitefield College", "short_name": "GWC", "type": "Private", "province": "Western Cape"},
        {"name": "Health and Fitness Professionals Academy", "short_name": "HFPA", "type": "Private", "province": "Western Cape"},
        {"name": "Helderberg College of Higher Education", "short_name": "Helderberg", "type": "Private", "province": "Western Cape"},
        {"name": "Henley Business School", "short_name": "Henley", "type": "Private", "province": "Gauteng"},
        {"name": "IHT Hotel School", "short_name": "IHT", "type": "Private", "province": "Western Cape"},
        {"name": "IMM Graduate School of Marketing", "short_name": "IMM", "type": "Private", "province": "Gauteng"},
        {"name": "The Independent Institute of Education", "short_name": "IIE", "type": "Private", "province": "Gauteng"},
        {"name": "Inscape Education Group", "short_name": "Inscape", "type": "Private", "province": "Gauteng"},
        {"name": "International Hotel School", "short_name": "IHS", "type": "Private", "province": "KwaZulu-Natal"},
        {"name": "International Trade Institute of Southern Africa", "short_name": "ITISA", "type": "Private", "province": "Gauteng"},
        {"name": "IQ Academy", "short_name": "IQ Academy", "type": "Private", "province": "Gauteng"},
        {"name": "Isa Carstens Academy", "short_name": "Isa Carstens", "type": "Private", "province": "Western Cape"},
        {"name": "Life Healthcare Group", "short_name": "Life Healthcare", "type": "Private", "province": "Gauteng"},
        {"name": "Lyceum College", "short_name": "Lyceum", "type": "Private", "province": "Gauteng"},
        {"name": "MANCOSA", "short_name": "MANCOSA", "type": "Private", "province": "KwaZulu-Natal"},
        {"name": "MEDICLINIC", "short_name": "Mediclinic", "type": "Private", "province": "Western Cape"},
        {"name": "Milpark Education", "short_name": "Milpark", "type": "Private", "province": "Gauteng"},
        {"name": "Mukhanyo Theological College", "short_name": "Mukhanyo", "type": "Private", "province": "Gauteng"},
        {"name": "Netcare Education", "short_name": "Netcare", "type": "Private", "province": "Gauteng"},
        {"name": "Newbridge Graduate Institute", "short_name": "Newbridge", "type": "Private", "province": "Gauteng"},
        {"name": "Oakfields College", "short_name": "Oakfields", "type": "Private", "province": "Gauteng"},
        {"name": "Open Learning Group", "short_name": "OLG", "type": "Private", "province": "Gauteng"},
        {"name": "The Open Window", "short_name": "Open Window", "type": "Private", "province": "Gauteng"},
        {"name": "Potchefstroom Academy", "short_name": "Potch Academy", "type": "Private", "province": "North West"},
        {"name": "Production Management Institute of Southern Africa", "short_name": "PMI", "type": "Private", "province": "Gauteng"},
        {"name": "Red and Yellow Creative School of Business", "short_name": "Red & Yellow", "type": "Private", "province": "Western Cape"},
        {"name": "Regenesys Education", "short_name": "Regenesys", "type": "Private", "province": "Gauteng"},
        {"name": "Regent Business School", "short_name": "Regent", "type": "Private", "province": "KwaZulu-Natal"},
        {"name": "Richfield Graduate Institute of Technology", "short_name": "Richfield", "type": "Private", "province": "KwaZulu-Natal"},
        {"name": "Ruth Prowse School of Art", "short_name": "Ruth Prowse", "type": "Private", "province": "Western Cape"},
        {"name": "SAE Institute of South Africa", "short_name": "SAE", "type": "Private", "province": "Western Cape"},
        {"name": "SANTS Private Higher Education Institution", "short_name": "SANTS", "type": "Private", "province": "Gauteng"},
        {"name": "Seth Mokitimi Methodist Seminary", "short_name": "SMMS", "type": "Private", "province": "KwaZulu-Natal"},
        {"name": "The South African College of Applied Psychology", "short_name": "SACAP", "type": "Private", "province": "Western Cape"},
        {"name": "South African School of Motion Picture Medium & Live Performance", "short_name": "AFDA", "type": "Private", "province": "Gauteng"},
        {"name": "South African Theological Seminary", "short_name": "SATS", "type": "Private", "province": "Gauteng"},
        {"name": "Southern Africa Bible College", "short_name": "SABC", "type": "Private", "province": "KwaZulu-Natal"},
        {"name": "Southern African Wildlife College", "short_name": "SAWC", "type": "Private", "province": "Limpopo"},
        {"name": "Stadio", "short_name": "Stadio", "type": "Private", "province": "Gauteng"},
        {"name": "St. Augustine College of South Africa", "short_name": "St Augustine", "type": "Private", "province": "Gauteng"},
        {"name": "Stellenbosch Academy of Design and Photography", "short_name": "Stellenbosch Academy", "type": "Private", "province": "Western Cape"},
        {"name": "Stenden South Africa BV", "short_name": "Stenden", "type": "Private", "province": "Eastern Cape"},
        {"name": "St John Vianney Seminary", "short_name": "SJV", "type": "Private", "province": "Gauteng"},
        {"name": "St Joseph's Theological Institute", "short_name": "SJTI", "type": "Private", "province": "KwaZulu-Natal"},
        {"name": "Theological Education by Extension College", "short_name": "TEEC", "type": "Private", "province": "Gauteng"},
        {"name": "The Swiss Hotel School SA", "short_name": "Swiss Hotel School", "type": "Private", "province": "Gauteng"},
        {"name": "TSIBA Education", "short_name": "TSIBA", "type": "Private", "province": "Western Cape"},
        {"name": "Union Bible Institute", "short_name": "UBI", "type": "Private", "province": "KwaZulu-Natal"},
        {"name": "Villioti Fashion Institute", "short_name": "Villioti", "type": "Private", "province": "Gauteng"},
    ]

    existing_names = {
        name for (name,) in session.query(Institution.name).all()
    }
    for data in institutions_data:
        if data["name"] not in existing_names:
            new_inst = Institution(**data)
            session.add(new_inst)
            existing_names.add(data["name"])
    
    session.commit()
    print(f"Institutions seeded successfully.")


def seed_bursaries(session: Session):
    """
    Idempotent seeding of Bursaries.
    """
    bursaries_data = [
        # --- Government ---
        {"name": "NSFAS Bursary", "provider": "Government (DHET)", "field_of_study": "All fields", "opening_date": date(2026, 9, 1), "closing_date": date(2027, 1, 31), "description": "National Student Financial Aid Scheme for academically deserving and financially needy students.", "website": "https://www.nsfas.org.za", "is_active": True},
        {"name": "Funza Lushaka Bursary", "provider": "Government (DBE)", "field_of_study": "Education", "opening_date": date(2026, 10, 1), "closing_date": date(2027, 1, 31), "description": "Bursary for students who want to pursue a teaching career in South Africa.", "website": "https://www.funzalushaka.doe.gov.za", "is_active": True},
        
        # --- Corporate ---
        {"name": "Sasol Bursary", "provider": "Sasol", "field_of_study": "Engineering, Science, Technology", "opening_date": date(2026, 4, 1), "closing_date": date(2026, 5, 17), "description": "Comprehensive bursary for undergraduate and postgraduate studies in STEM fields.", "website": "https://www.sasol.com/careers/bursaries", "is_active": True},
        {"name": "Old Mutual Actuarial Bursary", "provider": "Old Mutual", "field_of_study": "Actuarial Science", "opening_date": date(2026, 3, 1), "closing_date": date(2026, 8, 31), "description": "Prestigious bursary programme for future actuarial talent.", "website": "https://www.oldmutual.co.za/careers/bursaries", "is_active": True},
        {"name": "Sappi Bursary", "provider": "Sappi", "field_of_study": "Engineering, Forestry Science", "opening_date": date(2026, 7, 1), "closing_date": date(2026, 9, 30), "description": "Bursary for engineering and forestry science students.", "website": "https://www.sappi.com/careers/bursaries", "is_active": True},
        {"name": "MTN Bursary", "provider": "MTN", "field_of_study": "IT, Computer Science, Telecoms", "opening_date": date(2026, 6, 1), "closing_date": date(2026, 8, 31), "description": "Bursary for students in IT, Computer Science, and Telecommunications.", "website": "https://www.mtn.co.za/careers", "is_active": True},
        {"name": "Standard Bank IT Bursary", "provider": "Standard Bank", "field_of_study": "IT, Computer Science", "opening_date": date(2026, 8, 1), "closing_date": date(2026, 10, 31), "description": "Bursary for IT and Computer Science students.", "website": "https://www.standardbank.com/sbg/standard-bank-group/careers", "is_active": True},
        {"name": "Investec Bursary", "provider": "Investec", "field_of_study": "Commerce, Finance, IT", "opening_date": date(2026, 6, 1), "closing_date": date(2026, 9, 30), "description": "Bursary for students in commerce, finance, and IT fields.", "website": "https://www.investec.com/en_za/careers.html", "is_active": True},
        {"name": "Shoprite Bursary", "provider": "Shoprite", "field_of_study": "Retail, Commerce, IT", "opening_date": date(2026, 5, 1), "closing_date": date(2026, 9, 30), "description": "Bursary for retail, commerce, and IT students.", "website": "https://www.shoprite.co.za/careers", "is_active": True},
        {"name": "IDC Bursary", "provider": "Industrial Development Corporation", "field_of_study": "Engineering, Commerce, Science", "opening_date": date(2026, 6, 1), "closing_date": date(2026, 9, 30), "description": "Bursary for engineering, commerce, and science students.", "website": "https://www.idc.co.za/careers", "is_active": True},
        {"name": "Vodacom Bursary", "provider": "Vodacom", "field_of_study": "IT, Engineering, Commerce", "opening_date": date(2026, 6, 1), "closing_date": date(2026, 8, 31), "description": "Bursary for IT, engineering, and commerce students.", "website": "https://www.vodacom.co.za/careers", "is_active": True},
        {"name": "Capitec Bursary", "provider": "Capitec", "field_of_study": "Commerce, IT, Data Science", "opening_date": date(2026, 7, 1), "closing_date": date(2026, 10, 31), "description": "Bursary for commerce, IT, and data science students.", "website": "https://www.capitecbank.co.za/careers", "is_active": True},
        {"name": "Momentum Bursary", "provider": "Momentum", "field_of_study": "Actuarial Science, Finance", "opening_date": date(2026, 5, 1), "closing_date": date(2026, 9, 30), "description": "Bursary for actuarial science and finance students.", "website": "https://www.momentum.co.za/careers", "is_active": True},
        {"name": "Coronation Bursary", "provider": "Coronation Fund Managers", "field_of_study": "Finance, Actuarial Science", "opening_date": date(2026, 5, 1), "closing_date": date(2026, 8, 31), "description": "Bursary for finance and actuarial science students.", "website": "https://www.coronation.com/za/careers", "is_active": True},
        {"name": "Ninety One Bursary", "provider": "Ninety One", "field_of_study": "Finance, Investment", "opening_date": date(2026, 6, 1), "closing_date": date(2026, 9, 30), "description": "Bursary for finance and investment students.", "website": "https://www.ninetyone.com/careers", "is_active": True},
        {"name": "FirstRand Bursary", "provider": "FirstRand", "field_of_study": "Commerce, Finance, IT", "opening_date": date(2026, 6, 1), "closing_date": date(2026, 9, 30), "description": "Bursary for commerce, finance, and IT students.", "website": "https://www.firstrand.co.za/careers", "is_active": True},
        {"name": "CSIR Bursary", "provider": "CSIR", "field_of_study": "Science, Engineering, Technology", "opening_date": date(2026, 5, 1), "closing_date": date(2026, 8, 31), "description": "Bursary for science, engineering, and technology students.", "website": "https://www.csir.co.za/careers", "is_active": True},
        {"name": "Amazon Bursary", "provider": "Amazon", "field_of_study": "Computer Science, Engineering", "opening_date": date(2026, 6, 1), "closing_date": date(2026, 9, 30), "description": "Bursary for computer science and engineering students.", "website": "https://www.amazon.jobs/en/teams/internships-for-students", "is_active": True},
        {"name": "Samancor Bursary", "provider": "Samancor", "field_of_study": "Engineering, Mining, Science", "opening_date": date(2026, 5, 1), "closing_date": date(2026, 8, 31), "description": "Bursary for engineering, mining, and science students.", "website": "https://www.samancor.co.za/careers", "is_active": True},
        {"name": "DFFE Bursary", "provider": "Department of Forestry, Fisheries and the Environment", "field_of_study": "Environmental Science, Forestry", "opening_date": date(2026, 6, 1), "closing_date": date(2026, 9, 30), "description": "Bursary for environmental science and forestry students.", "website": "https://www.dffe.gov.za/careers", "is_active": True},
        {"name": "Harmony Gold Bursary", "provider": "Harmony Gold", "field_of_study": "Engineering, Mining, Geology", "opening_date": date(2026, 5, 1), "closing_date": date(2026, 8, 31), "description": "Bursary for engineering, mining, and geology students.", "website": "https://www.harmony.co.za/careers", "is_active": True},
        {"name": "HP Bursary", "provider": "HP", "field_of_study": "IT, Computer Science, Engineering", "opening_date": date(2026, 6, 1), "closing_date": date(2026, 9, 30), "description": "Bursary for IT, computer science, and engineering students.", "website": "https://www.hp.com/za-en/careers", "is_active": True},
        {"name": "AGSA/Solarpop Bursary", "provider": "Auditor-General of South Africa", "field_of_study": "Accounting, Auditing", "opening_date": date(2026, 5, 1), "closing_date": date(2026, 8, 31), "description": "Bursary for accounting and auditing students.", "website": "https://www.agsa.co.za/careers", "is_active": True},
        {"name": "Free State Govt Bursary", "provider": "Free State Provincial Government", "field_of_study": "Various", "opening_date": date(2026, 6, 1), "closing_date": date(2026, 9, 30), "description": "Bursary for students from the Free State province.", "website": "https://www.fs.gov.za", "is_active": True},
        {"name": "LDARD Bursary", "provider": "Limpopo Department of Agriculture and Rural Development", "field_of_study": "Agriculture, Rural Development", "opening_date": date(2026, 5, 1), "closing_date": date(2026, 8, 31), "description": "Bursary for agriculture and rural development students.", "website": "https://www.ldard.gov.za", "is_active": True},
        
        # --- Professional ---
        {"name": "SAICA Thuthuka Bursary", "provider": "SAICA", "field_of_study": "Accounting (CA stream)", "opening_date": date(2026, 3, 1), "closing_date": date(2026, 8, 31), "description": "Bursary for aspiring Chartered Accountants (CA(SA)).", "website": "https://www.saica.co.za", "is_active": True},
        {"name": "SAIPA Bursary", "provider": "SAIPA", "field_of_study": "Accounting (Professional Accountant)", "opening_date": date(2026, 4, 1), "closing_date": date(2026, 9, 30), "description": "Bursary for aspiring Professional Accountants.", "website": "https://www.saipa.co.za", "is_active": True},

        # --- SETA ---
        {"name": "BANKSETA Bursary", "provider": "BANKSETA", "field_of_study": "Banking, Finance", "opening_date": date(2026, 5, 1), "closing_date": date(2026, 9, 30), "description": "Bursary for banking and finance students.", "website": "https://www.bankseta.org.za", "is_active": True},
        {"name": "MQA Bursary", "provider": "Mining Qualifications Authority", "field_of_study": "Mining, Engineering", "opening_date": date(2026, 5, 1), "closing_date": date(2026, 8, 31), "description": "Bursary for mining and engineering students.", "website": "https://www.mqa.org.za", "is_active": True},
        {"name": "HWSETA Bursary", "provider": "Health and Welfare SETA", "field_of_study": "Health Sciences, Social Work", "opening_date": date(2026, 5, 1), "closing_date": date(2026, 8, 31), "description": "Bursary for health sciences and social work students.", "website": "https://www.hwseta.org.za", "is_active": True},
        {"name": "INSETA Bursary", "provider": "Insurance SETA", "field_of_study": "Insurance, Risk Management", "opening_date": date(2026, 5, 1), "closing_date": date(2026, 9, 30), "description": "Bursary for insurance and risk management students.", "website": "https://www.inseta.org.za", "is_active": True},
        {"name": "TETA Bursary", "provider": "Transport Education Training Authority", "field_of_study": "Transport, Logistics", "opening_date": date(2026, 5, 1), "closing_date": date(2026, 8, 31), "description": "Bursary for transport and logistics students.", "website": "https://www.teta.org.za", "is_active": True},
        {"name": "W&RSETA Bursary", "provider": "Wholesale and Retail SETA", "field_of_study": "Retail, Wholesale", "opening_date": date(2026, 5, 1), "closing_date": date(2026, 9, 30), "description": "Bursary for retail and wholesale students.", "website": "https://www.wrseta.org.za", "is_active": True},
        {"name": "ETDP SETA Bursary", "provider": "Education, Training and Development Practices SETA", "field_of_study": "Education, Training", "opening_date": date(2026, 5, 1), "closing_date": date(2026, 8, 31), "description": "Bursary for education and training students.", "website": "https://www.etdpseta.org.za", "is_active": True},
        {"name": "SASSETA Bursary", "provider": "Safety and Security SETA", "field_of_study": "Safety, Security, Law", "opening_date": date(2026, 5, 1), "closing_date": date(2026, 8, 31), "description": "Bursary for safety, security, and law students.", "website": "https://www.sasseta.org.za", "is_active": True},
        {"name": "AgriSETA Bursary", "provider": "Agricultural SETA", "field_of_study": "Agriculture", "opening_date": date(2026, 5, 1), "closing_date": date(2026, 8, 31), "description": "Bursary for agriculture students.", "website": "https://www.agriseta.co.za", "is_active": True},

        # --- NGO/Foundation ---
        {"name": "Mandela Rhodes Scholarship", "provider": "Mandela Rhodes Foundation", "field_of_study": "Postgraduate (Honours/Master's)", "opening_date": date(2026, 1, 15), "closing_date": date(2026, 4, 14), "description": "Prestigious scholarship for postgraduate studies in South Africa.", "website": "https://www.mandelarhodes.org", "is_active": True},
        {"name": "Allan Gray Orbis Fellowship", "provider": "Allan Gray Orbis Foundation", "field_of_study": "Commerce, Science, Engineering, Law, Humanities, Arts, Health", "opening_date": date(2026, 2, 1), "closing_date": date(2026, 5, 31), "description": "Fellowship for entrepreneurial students at partner universities.", "website": "https://www.allangrayorbis.org", "is_active": True},
        {"name": "Dell Young Leaders", "provider": "Michael & Susan Dell Foundation", "field_of_study": "All fields (Invitation only)", "opening_date": date(2026, 1, 1), "closing_date": date(2026, 3, 31), "description": "Invitation-only scholarship for first-year NSFAS-eligible students at UCT and UP.", "website": "https://www.dell.org", "is_active": True},
    ]

    existing_names = {
        name for (name,) in session.query(Bursary.name).all()
    }
    for data in bursaries_data:
        if data["name"] not in existing_names:
            new_bursary = Bursary(**data)
            session.add(new_bursary)
            existing_names.add(data["name"])
    
    session.commit()
    print(f"Bursaries seeded successfully.")


def seed_programmes(session: Session):
    """
    Seeds university, TVET, and private programmes into the shared Programme table.
    """
    programme_sources = (
        ("University", university_data),
        ("TVET", tvet_data),
        ("Private", private_data),
    )
    institution_types = {}
    for institution_type, records in programme_sources:
        for record in records:
            institution_types.setdefault(record["institution"], institution_type)

    existing_institution_names = {
        name for (name,) in session.query(Institution.name).all()
    }
    for name, institution_type in institution_types.items():
        if name not in existing_institution_names:
            session.add(Institution(
                name=name,
                short_name=None,
                type=institution_type,
                province=None,
            ))
            existing_institution_names.add(name)

    session.flush()

    # Remove only the temporary demo records previously inserted by this project.
    session.query(Programme).filter(
        Programme.source == "EduAccess example listing"
    ).delete(synchronize_session=False)

    programme_by_key = {
        (programme.institution, programme.programme): programme
        for programme in session.query(Programme).all()
    }
    inserted = 0
    updated = 0
    for _, records in programme_sources:
        for data in records:
            values = {
                "faculty": data.get("faculty"),
                "department": data.get("department"),
                "score_type": data.get("score_type"),
                "aps_score": data.get("aps_score"),
                "max_score": data.get("max_score"),
                "entry_requirement": data.get("entry_requirement") or data.get("notes"),
                "notes": data.get("notes"),
                "source": data.get("source"),
            }
            key = (data["institution"], data["programme"])
            existing = programme_by_key.get(key)

            if existing is None:
                existing = Programme(
                    institution=data["institution"],
                    programme=data["programme"],
                    **values,
                )
                session.add(existing)
                programme_by_key[key] = existing
                inserted += 1
                continue

            for field, value in values.items():
                setattr(existing, field, value)
            updated += 1

    session.commit()
    print(
        f"Programmes seeded: {inserted} added, {updated} updated "
        f"from university, TVET, and private datasets."
    )


def seed_all(session: Session):
    """Main entry point to seed all data."""
    print("Starting seed process...")
    seed_institutions(session)
    seed_bursaries(session)
    seed_programmes(session)  # <-- Added this
    print("Seed process complete.")

if __name__ == "__main__":
    initialize_schema()
    with SessionLocal() as session:
        print("Seeding database...")
        seed_all(session)
    print("Database seeding complete.")
