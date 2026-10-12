import time
from pathlib import Path
from playwright.sync_api import sync_playwright

output_dir = Path(r"D:\RealEstate_Analysis_Screenshots")
output_dir.mkdir(parents=True, exist_ok=True)

# Clean up any test files
for f in output_dir.glob("test_*.png"):
    try:
        f.unlink()
    except Exception:
        pass

dashboard_url = "file:///D:/three/RealEstate_analysis/dashboard/index.html"

def run_captures():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        # 1920x1080 Full HD crisp viewport
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(dashboard_url)
        page.wait_for_timeout(3000)

        tasks = [
            # 1. Slide 1 Part 1
            {
                "file": "01_Executive_Market_Briefing.png",
                "setup": lambda pg: (
                    pg.evaluate("switchMainSection('operations')"),
                    pg.evaluate("goToSlide(1)"),
                    pg.evaluate("switchOpSubpage(1, 1)"),
                    pg.wait_for_timeout(1500)
                )
            },
            # 2. Slide 1 Part 2
            {
                "file": "02_Delivery_Forecast_Finishing_Composition.png",
                "setup": lambda pg: (
                    pg.evaluate("goToSlide(1)"),
                    pg.evaluate("switchOpSubpage(1, 2)"),
                    pg.wait_for_timeout(1500)
                )
            },
            # 3. Slide 2 Part 1 (GIS Map)
            {
                "file": "03_Geospatial_GIS_Supply_Density_Map.png",
                "setup": lambda pg: (
                    pg.evaluate("goToSlide(2)"),
                    pg.evaluate("switchOpSubpage(2, 1)"),
                    pg.wait_for_timeout(2500)
                )
            },
            # 4. Slide 2 Part 2 (Growth Corridors)
            {
                "file": "04_Geospatial_Growth_Corridors_Validation.png",
                "setup": lambda pg: (
                    pg.evaluate("goToSlide(2)"),
                    pg.evaluate("switchOpSubpage(2, 2)"),
                    pg.wait_for_timeout(1500)
                )
            },
            # 5. Slide 3 Part 2 (Price Waterfall & Elasticity)
            {
                "file": "05_Price_Dynamics_Waterfall_Elasticity.png",
                "setup": lambda pg: (
                    pg.evaluate("goToSlide(3)"),
                    pg.evaluate("switchOpSubpage(3, 2)"),
                    pg.wait_for_timeout(1500)
                )
            },
            # 6. Slide 4 Part 1 (Bank Financing Pre-qualification)
            {
                "file": "06_Bank_Financing_Mortgage_PreQualification.png",
                "setup": lambda pg: (
                    pg.evaluate("goToSlide(4)"),
                    pg.evaluate("switchOpSubpage(4, 1)"),
                    pg.wait_for_timeout(1500)
                )
            },
            # 7. Slide 4 Part 2 (Amortization & Equity Simulator)
            {
                "file": "07_Bank_Amortization_Schedule_Equity_Simulator.png",
                "setup": lambda pg: (
                    pg.evaluate("goToSlide(4)"),
                    pg.evaluate("switchOpSubpage(4, 2)"),
                    pg.wait_for_timeout(1500)
                )
            },
            # 8. Slide 5 Part 1 (Quality Score & Environmental AQI)
            {
                "file": "08_Quality_Score_Matrix_Environmental_AQI.png",
                "setup": lambda pg: (
                    pg.evaluate("goToSlide(5)"),
                    pg.evaluate("switchOpSubpage(5, 1)"),
                    pg.wait_for_timeout(1500)
                )
            },
            # 9. Slide 6 Part 1 (Market Economics & Types)
            {
                "file": "09_Market_Economics_Property_Distribution.png",
                "setup": lambda pg: (
                    pg.evaluate("goToSlide(6)"),
                    pg.evaluate("switchOpSubpage(6, 1)"),
                    pg.wait_for_timeout(1500)
                )
            },
            # 10. Slide 7 Part 1 (Architectural Dimensions)
            {
                "file": "10_Architectural_Dimensions_Room_Sanitary_Matrix.png",
                "setup": lambda pg: (
                    pg.evaluate("goToSlide(7)"),
                    pg.evaluate("switchOpSubpage(7, 1)"),
                    pg.wait_for_timeout(1500)
                )
            },
            # 11. Slide 8 Part 1 (Inventory Registry Data Table)
            {
                "file": "11_Audited_Inventory_Explorer_Data_Grid.png",
                "setup": lambda pg: (
                    pg.evaluate("goToSlide(8)"),
                    pg.evaluate("switchOpSubpage(8, 1)"),
                    pg.wait_for_timeout(1500)
                )
            },
            # 12. Modal Deep-Dive Audit
            {
                "file": "12_Property_DeepDive_Unit_Audit_Modal.png",
                "setup": lambda pg: (
                    pg.evaluate("goToSlide(8)"),
                    pg.evaluate("openRecordModal(0)"),
                    pg.wait_for_timeout(1500)
                )
            },
            # 13. Statistics Slide 1 (BI Gauges & Tiers)
            {
                "file": "13_BI_Statistics_Market_Overview_Gauges.png",
                "setup": lambda pg: (
                    pg.evaluate("closeModalDirect()"),
                    pg.evaluate("switchMainSection('statistics')"),
                    pg.evaluate("goToStatSlide(1)"),
                    pg.wait_for_timeout(2000)
                )
            },
            # 14. Statistics Slide 4 (Location Volume & PPM)
            {
                "file": "14_BI_Location_Analysis_PPM_Compound_Penetration.png",
                "setup": lambda pg: (
                    pg.evaluate("goToStatSlide(4)"),
                    pg.wait_for_timeout(1800)
                )
            },
            # 15. Statistics Slide 5 (Econometrics & Boxplots)
            {
                "file": "15_BI_Econometrics_Price_Distribution_Boxplots.png",
                "setup": lambda pg: (
                    pg.evaluate("goToStatSlide(5)"),
                    pg.wait_for_timeout(1800)
                )
            },
        ]

        for i, t in enumerate(tasks, start=1):
            target_path = output_dir / t["file"]
            print(f"[{i}/15] Capturing {t['file']}...")
            t["setup"](page)
            page.screenshot(path=str(target_path), full_page=False)
            print(f"       Saved: {target_path} ({target_path.stat().st_size} bytes)")

        browser.close()
        print("\nAll 15 screenshots successfully captured and saved to D:\\RealEstate_Analysis_Screenshots!")

if __name__ == "__main__":
    run_captures()
