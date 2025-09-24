#!/usr/bin/env python3
"""
Populate Company Data Script
Tech-028: API Implementation

This script populates the companies table with proper company names, sectors, and other details
for all German DAX companies that currently have placeholder data.
"""

import asyncio
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

# German DAX 40 companies with proper data
DAX_COMPANIES_DATA = {
    "1COV.DE": {
        "name": "Covestro AG",
        "sector": "Materials",
        "industry": "Chemicals",
        "description": "Covestro is a leading manufacturer of high-tech polymer materials.",
        "employee_count": 18000,
        "market_cap": 8.5e9,
        "website": "https://www.covestro.com",
    },
    "ADS.DE": {
        "name": "Adidas AG",
        "sector": "Consumer Discretionary",
        "industry": "Footwear & Apparel",
        "description": "Adidas is a multinational corporation, founded and headquartered in Germany, that designs and manufactures shoes, clothing and accessories.",
        "employee_count": 60000,
        "market_cap": 45.2e9,
        "website": "https://www.adidas.com",
    },
    "ALV.DE": {
        "name": "Allianz SE",
        "sector": "Financial Services",
        "industry": "Insurance",
        "description": "Allianz is a German multinational financial services company headquartered in Munich, Germany.",
        "employee_count": 150000,
        "market_cap": 95.8e9,
        "website": "https://www.allianz.com",
    },
    "BAS.DE": {
        "name": "BASF SE",
        "sector": "Materials",
        "industry": "Chemicals",
        "description": "BASF is a German multinational chemical company and the largest chemical producer in the world.",
        "employee_count": 110000,
        "market_cap": 75.3e9,
        "website": "https://www.basf.com",
    },
    "BAYN.DE": {
        "name": "Bayer AG",
        "sector": "Healthcare",
        "industry": "Pharmaceuticals",
        "description": "Bayer is a German multinational pharmaceutical and biotechnology company.",
        "employee_count": 100000,
        "market_cap": 65.2e9,
        "website": "https://www.bayer.com",
    },
    "BEI.DE": {
        "name": "Beiersdorf AG",
        "sector": "Consumer Staples",
        "industry": "Personal Care",
        "description": "Beiersdorf is a German multinational personal care company.",
        "employee_count": 20000,
        "market_cap": 28.5e9,
        "website": "https://www.beiersdorf.com",
    },
    "BMW.DE": {
        "name": "BMW AG",
        "sector": "Consumer Discretionary",
        "industry": "Automotive",
        "description": "Bayerische Motoren Werke AG, commonly referred to as BMW, is a German multinational corporation.",
        "employee_count": 130000,
        "market_cap": 55.7e9,
        "website": "https://www.bmw.com",
    },
    "CBK.DE": {
        "name": "Commerzbank AG",
        "sector": "Financial Services",
        "industry": "Banking",
        "description": "Commerzbank is a major German bank operating as a universal bank.",
        "employee_count": 50000,
        "market_cap": 8.9e9,
        "website": "https://www.commerzbank.com",
    },
    "CON.DE": {
        "name": "Continental AG",
        "sector": "Consumer Discretionary",
        "industry": "Automotive Parts",
        "description": "Continental is a German multinational automotive parts manufacturing company.",
        "employee_count": 240000,
        "market_cap": 12.5e9,
        "website": "https://www.continental.com",
    },
    "DAI.DE": {
        "name": "Daimler Truck Holding AG",
        "sector": "Consumer Discretionary",
        "industry": "Commercial Vehicles",
        "description": "Daimler Truck is a German multinational truck manufacturer.",
        "employee_count": 100000,
        "market_cap": 25.3e9,
        "website": "https://www.daimlertruck.com",
    },
    "DB1.DE": {
        "name": "Deutsche Börse AG",
        "sector": "Financial Services",
        "industry": "Financial Exchanges",
        "description": "Deutsche Börse is a German multinational marketplace organizer for the trading of shares and other securities.",
        "employee_count": 6000,
        "market_cap": 35.8e9,
        "website": "https://www.deutsche-boerse.com",
    },
    "DBK.DE": {
        "name": "Deutsche Bank AG",
        "sector": "Financial Services",
        "industry": "Banking",
        "description": "Deutsche Bank is a German multinational investment bank and financial services company.",
        "employee_count": 85000,
        "market_cap": 18.5e9,
        "website": "https://www.deutsche-bank.com",
    },
    "DHER.DE": {
        "name": "Delivery Hero SE",
        "sector": "Consumer Discretionary",
        "industry": "Food Delivery",
        "description": "Delivery Hero is a German multinational online food ordering and delivery platform.",
        "employee_count": 15000,
        "market_cap": 12.8e9,
        "website": "https://www.deliveryhero.com",
    },
    "DPW.DE": {
        "name": "Deutsche Post AG",
        "sector": "Industrials",
        "industry": "Logistics",
        "description": "Deutsche Post is a German multinational package delivery and supply chain management company.",
        "employee_count": 550000,
        "market_cap": 45.2e9,
        "website": "https://www.deutschepost.com",
    },
    "DTE.DE": {
        "name": "Deutsche Telekom AG",
        "sector": "Communication Services",
        "industry": "Telecommunications",
        "description": "Deutsche Telekom is a German telecommunications company headquartered in Bonn.",
        "employee_count": 220000,
        "market_cap": 95.5e9,
        "website": "https://www.telekom.com",
    },
    "ENR.DE": {
        "name": "Siemens Energy AG",
        "sector": "Industrials",
        "industry": "Energy Equipment",
        "description": "Siemens Energy is a German multinational energy technology company.",
        "employee_count": 90000,
        "market_cap": 15.8e9,
        "website": "https://www.siemens-energy.com",
    },
    "EOAN.DE": {
        "name": "E.ON SE",
        "sector": "Utilities",
        "industry": "Electric Utilities",
        "description": "E.ON is a German multinational electric utility company.",
        "employee_count": 75000,
        "market_cap": 28.5e9,
        "website": "https://www.eon.com",
    },
    "FME.DE": {
        "name": "Fresenius Medical Care AG",
        "sector": "Healthcare",
        "industry": "Medical Devices",
        "description": "Fresenius Medical Care is a German multinational healthcare company.",
        "employee_count": 120000,
        "market_cap": 12.5e9,
        "website": "https://www.freseniusmedicalcare.com",
    },
    "FRE.DE": {
        "name": "Fresenius SE",
        "sector": "Healthcare",
        "industry": "Healthcare Services",
        "description": "Fresenius is a German multinational healthcare company.",
        "employee_count": 300000,
        "market_cap": 18.5e9,
        "website": "https://www.fresenius.com",
    },
    "HEN3.DE": {
        "name": "Henkel AG & Co. KGaA",
        "sector": "Consumer Staples",
        "industry": "Household Products",
        "description": "Henkel is a German multinational chemical and consumer goods company.",
        "employee_count": 52000,
        "market_cap": 35.8e9,
        "website": "https://www.henkel.com",
    },
    "HNR1.DE": {
        "name": "Hannover Rück SE",
        "sector": "Financial Services",
        "industry": "Reinsurance",
        "description": "Hannover Re is a German multinational reinsurance company.",
        "employee_count": 3000,
        "market_cap": 8.5e9,
        "website": "https://www.hannover-re.com",
    },
    "IFX.DE": {
        "name": "Infineon Technologies AG",
        "sector": "Technology",
        "industry": "Semiconductors",
        "description": "Infineon Technologies is a German multinational semiconductor company.",
        "employee_count": 50000,
        "market_cap": 45.2e9,
        "website": "https://www.infineon.com",
    },
    "LIN.DE": {
        "name": "Linde plc",
        "sector": "Materials",
        "industry": "Industrial Gases",
        "description": "Linde is a German multinational chemical company.",
        "employee_count": 80000,
        "market_cap": 185.5e9,
        "website": "https://www.linde.com",
    },
    "MRK.DE": {
        "name": "Merck KGaA",
        "sector": "Healthcare",
        "industry": "Pharmaceuticals",
        "description": "Merck KGaA is a German multinational pharmaceutical, chemical and life sciences company.",
        "employee_count": 60000,
        "market_cap": 75.3e9,
        "website": "https://www.merckgroup.com",
    },
    "MTX.DE": {
        "name": "MTU Aero Engines AG",
        "sector": "Industrials",
        "industry": "Aerospace & Defense",
        "description": "MTU Aero Engines is a German aircraft engine manufacturer.",
        "employee_count": 11000,
        "market_cap": 8.9e9,
        "website": "https://www.mtu.de",
    },
    "MUV2.DE": {
        "name": "Münchener Rückversicherungs-Gesellschaft AG",
        "sector": "Financial Services",
        "industry": "Reinsurance",
        "description": "Munich Re is a German multinational reinsurance company.",
        "employee_count": 40000,
        "market_cap": 28.5e9,
        "website": "https://www.munichre.com",
    },
    "PUM.DE": {
        "name": "Puma SE",
        "sector": "Consumer Discretionary",
        "industry": "Footwear & Apparel",
        "description": "Puma is a German multinational corporation that designs and manufactures athletic and casual footwear, apparel and accessories.",
        "employee_count": 16000,
        "market_cap": 12.8e9,
        "website": "https://www.puma.com",
    },
    "QGEN.DE": {
        "name": "Qiagen N.V.",
        "sector": "Healthcare",
        "industry": "Biotechnology",
        "description": "Qiagen is a German multinational biotechnology company.",
        "employee_count": 5000,
        "market_cap": 8.5e9,
        "website": "https://www.qiagen.com",
    },
    "RWE.DE": {
        "name": "RWE AG",
        "sector": "Utilities",
        "industry": "Electric Utilities",
        "description": "RWE is a German multinational energy company.",
        "employee_count": 20000,
        "market_cap": 25.3e9,
        "website": "https://www.rwe.com",
    },
    "SAP.DE": {
        "name": "SAP SE",
        "sector": "Technology",
        "industry": "Software",
        "description": "SAP is a German multinational software corporation.",
        "employee_count": 110000,
        "market_cap": 185.5e9,
        "website": "https://www.sap.com",
    },
    "SHL.DE": {
        "name": "Siemens Healthineers AG",
        "sector": "Healthcare",
        "industry": "Medical Devices",
        "description": "Siemens Healthineers is a German multinational medical technology company.",
        "employee_count": 50000,
        "market_cap": 45.2e9,
        "website": "https://www.siemens-healthineers.com",
    },
    "SIE.DE": {
        "name": "Siemens AG",
        "sector": "Industrials",
        "industry": "Industrial Conglomerates",
        "description": "Siemens is a German multinational conglomerate company and the largest industrial manufacturing company in Europe.",
        "employee_count": 300000,
        "market_cap": 125.8e9,
        "website": "https://www.siemens.com",
    },
    "SY1.DE": {
        "name": "Symrise AG",
        "sector": "Materials",
        "industry": "Specialty Chemicals",
        "description": "Symrise is a German multinational corporation that creates fragrances, flavorings, cosmetic active ingredients and raw materials.",
        "employee_count": 10000,
        "market_cap": 15.8e9,
        "website": "https://www.symrise.com",
    },
    "VNA.DE": {
        "name": "Vonovia SE",
        "sector": "Real Estate",
        "industry": "Real Estate Investment Trusts",
        "description": "Vonovia is a German real estate company and the largest residential real estate company in Europe.",
        "employee_count": 12000,
        "market_cap": 18.5e9,
        "website": "https://www.vonovia.de",
    },
    "VOW3.DE": {
        "name": "Volkswagen AG",
        "sector": "Consumer Discretionary",
        "industry": "Automotive",
        "description": "Volkswagen is a German multinational automotive manufacturing company.",
        "employee_count": 670000,
        "market_cap": 95.5e9,
        "website": "https://www.volkswagen.com",
    },
    "WCH.DE": {
        "name": "Wacker Chemie AG",
        "sector": "Materials",
        "industry": "Chemicals",
        "description": "Wacker Chemie is a German multinational chemical company.",
        "employee_count": 15000,
        "market_cap": 8.9e9,
        "website": "https://www.wacker.com",
    },
    "ZAL.DE": {
        "name": "Zalando SE",
        "sector": "Consumer Discretionary",
        "industry": "E-commerce",
        "description": "Zalando is a German multinational e-commerce company.",
        "employee_count": 17000,
        "market_cap": 12.5e9,
        "website": "https://www.zalando.com",
    },
}


async def update_company_data():
    """Update company data in the database with proper information."""
    try:
        # Connect to database
        conn = sqlite3.connect("/app/db/investbyyourself_dev.db")
        cursor = conn.cursor()

        print("🔄 Updating company data...")

        updated_count = 0
        for symbol, data in DAX_COMPANIES_DATA.items():
            try:
                # Update company information
                cursor.execute(
                    """
                    UPDATE companies
                    SET name = ?,
                        sector = ?,
                        industry = ?,
                        description = ?,
                        employee_count = ?,
                        market_cap = ?,
                        website = ?,
                        updated_at = ?
                    WHERE symbol = ?
                """,
                    (
                        data["name"],
                        data["sector"],
                        data["industry"],
                        data["description"],
                        data["employee_count"],
                        data["market_cap"],
                        data["website"],
                        datetime.now(),
                        symbol,
                    ),
                )

                if cursor.rowcount > 0:
                    updated_count += 1
                    print(f"✅ Updated {symbol}: {data['name']}")
                else:
                    print(f"⚠️  No rows updated for {symbol}")

            except Exception as e:
                print(f"❌ Error updating {symbol}: {str(e)}")

        # Commit changes
        conn.commit()

        # Verify updates
        cursor.execute("SELECT COUNT(*) FROM companies WHERE name NOT LIKE 'Company %'")
        proper_companies = cursor.fetchone()[0]

        cursor.execute(
            "SELECT symbol, name, sector FROM companies WHERE name NOT LIKE 'Company %' ORDER BY symbol"
        )
        companies = cursor.fetchall()

        print(f"\n📊 Database Update Summary:")
        print(f"   Total companies: {len(DAX_COMPANIES_DATA)}")
        print(f"   Updated companies: {updated_count}")
        print(f"   Companies with proper data: {proper_companies}")

        print(f"\n📋 Updated Companies:")
        for symbol, name, sector in companies:
            print(f"   {symbol:<8} - {name:<30} | {sector}")

        conn.close()
        print(f"\n✅ Company data update completed successfully!")

    except Exception as e:
        print(f"❌ Error updating company data: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(update_company_data())
