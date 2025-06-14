import flet as ft
import os
import subprocess
import platform
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio

# Data classes untuk struktur data
@dataclass
class ApplicantData:
    id: int
    name: str
    cv_path: str
    email: str
    phone: str
    address: str
    birthdate: str
    matched_keywords: Dict[str, int]
    total_matches: int
    application_role: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = None
    job_history: List[Dict] = None
    education: List[Dict] = None

# Kontrol Kustom untuk Kartu CV
class CVCard(ft.Card):
    def __init__(self, applicant_data: ApplicantData, on_summary_click, on_view_cv_click):
        super().__init__()
        self.applicant_data = applicant_data
        self.on_summary_click = on_summary_click
        self.on_view_cv_click = on_view_cv_click
        
        # Styling kartu
        self.elevation = 4
        self.margin = ft.margin.symmetric(vertical=5)
        
        # Buat konten kartu
        self._build_content()
    

    def _build_content(self):
        # Buat daftar kata kunci yang cocok
        keyword_widgets = []
        for keyword, count in self.applicant_data.matched_keywords.items():
            keyword_widgets.append(
                ft.Text(
                    f"{keyword}: {count} occurrence{'s' if count > 1 else ''}",
                    size=12,
                    color=ft.Colors.BLUE_800  # Changed from BLUE_GREY_600 to deeper blue
                )
            )
        
        # Tombol aksi
        action_buttons = ft.Row(
            controls=[
                ft.TextButton(
                    text="Summary",
                    icon=ft.Icons.INFO,
                    on_click=lambda _: self.on_summary_click(self.applicant_data.id),
                    style=ft.ButtonStyle(
                        color=ft.Colors.INDIGO_700,
                        bgcolor=ft.Colors.INDIGO_50
                    )
                ),
                ft.TextButton(
                    text="View CV",
                    icon=ft.Icons.VISIBILITY,
                    on_click=lambda _: self.on_view_cv_click(self.applicant_data.cv_path),
                    style=ft.ButtonStyle(
                        color=ft.Colors.TEAL_700,
                        bgcolor=ft.Colors.TEAL_50
                    )
                )
            ],
            alignment=ft.MainAxisAlignment.END,
            spacing=10
        )
        
        # Konten utama kartu
        self.content = ft.Container(
            padding=15,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Text(
                        self.applicant_data.name,
                        weight=ft.FontWeight.BOLD,
                        size=18,
                        color=ft.Colors.GREY_900  # Added for better contrast
                    ),
                    ft.Text(
                        f"Matched Keywords: {self.applicant_data.total_matches}",
                        size=14,
                        color=ft.Colors.GREEN_700,  # Changed from GREEN_700 to more vibrant
                        weight=ft.FontWeight.W_600
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_300),  # Changed from OUTLINE_VARIANT
                    ft.Column(
                        spacing=4,
                        controls=keyword_widgets
                    ),
                    action_buttons
                ]
            ),
            bgcolor=ft.Colors.WHITE,  # Added white background
            border_radius=12,
            border=ft.border.all(1, ft.Colors.GREY_200)
        )

# Kelas utama aplikasi ATS
class ATSApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "CV Analyzer App"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.padding = 20
        
        # State aplikasi
        self.search_keywords = ""
        self.selected_algorithm = "KMP"
        self.top_matches = "10"
        self.search_results: List[ApplicantData] = []
        self.is_searching = False
        self.current_applicant: Optional[ApplicantData] = None
        
        # Waktu eksekusi
        self.exact_match_time = ""
        self.fuzzy_match_time = ""
        
        # Setup routing
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop
        
        # Inisialisasi views
        self.init_views()
        
        # Mulai dengan halaman pencarian
        self.page.go("/search")
    
    def init_views(self):
        """Inisialisasi semua views"""
        pass
    
    def route_change(self, route):
        """Handler untuk perubahan route"""
        self.page.views.clear()
        
        if self.page.route == "/search":
            self.page.views.append(self.build_search_view())
        elif self.page.route.startswith("/summary/"):
            # Extract applicant ID from route
            try:
                applicant_id = int(self.page.route.split("/")[-1])
                self.page.views.append(self.build_summary_view(applicant_id))
            except (ValueError, IndexError):
                self.page.go("/search")
                return
        else:
            self.page.go("/search")
            return
        
        self.page.update()
    
    def view_pop(self, view):
        """Handler untuk pop view (tombol back)"""
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)
    
    def build_search_view(self) -> ft.View:
        """Membangun tampilan pencarian utama"""
        # Kontrol input
        keywords_field = ft.TextField(
            label="Keywords",
            hint_text="e.g., Python, React, SQL",
            expand=True,
            value=self.search_keywords,
            on_change=self.on_keywords_change,
            on_submit=self.on_search_click,
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_600,
            label_style=ft.TextStyle(color=ft.Colors.BLUE_700)
        )
        
        algorithm_radio = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(
                    value="KMP", 
                    label="Knuth-Morris-Pratt (KMP)",
                    active_color=ft.Colors.PURPLE_600
                ),
                ft.Radio(
                    value="BM", 
                    label="Boyer-Moore (BM)",
                    active_color=ft.Colors.PURPLE_600
                )
            ]),
            value=self.selected_algorithm,
            on_change=self.on_algorithm_change
        )
        
        top_matches_dropdown = ft.Dropdown(
            label="Top Matches",
            options=[
                ft.dropdown.Option("5"),
                ft.dropdown.Option("10"),
                ft.dropdown.Option("20"),
                ft.dropdown.Option("50")
            ],
            value=self.top_matches,
            width=150,
            on_change=self.on_top_matches_change,
            border_color=ft.Colors.INDIGO_400,
            focused_border_color=ft.Colors.INDIGO_600
        )
        
        search_button = ft.ElevatedButton(
            text="Search",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search_click,
            style=ft.ButtonStyle(
                shape=ft.StadiumBorder(),
                bgcolor=ft.Colors.BLUE_600,  # Changed from default
                color=ft.Colors.WHITE,
                elevation=4
            ),
            disabled=self.is_searching
        )
        
        # Progress indicator
        progress_indicator = ft.ProgressRing(
            visible=self.is_searching,
            width=30,
            height=30,
            color=ft.Colors.BLUE_600
        )
        
        # Summary result section
        summary_section = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Search Results Summary:", 
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_800
                ),
                ft.Text(
                    f"Exact Match Time: {self.exact_match_time}", 
                    data="exact_time",
                    color=ft.Colors.GREEN_700
                ),
                ft.Text(
                    f"Fuzzy Match Time: {self.fuzzy_match_time}", 
                    data="fuzzy_time",
                    color=ft.Colors.ORANGE_700
                )
            ]),
            visible=bool(self.exact_match_time or self.fuzzy_match_time),
            padding=15,
            border_radius=12,
            bgcolor=ft.Colors.BLUE_GREY_50,  # Changed from BLUE_GREY_50
            border=ft.border.all(1, ft.Colors.BLUE_GREY_200)
        )
        
        # Results container
        results_container = ft.ListView(
            expand=True,
            spacing=10,
            padding=10,
            controls=[CVCard(result, self.on_summary_click, self.on_view_cv_click) 
                     for result in self.search_results]
        )
        
        # Layout utama
        main_content = ft.Column(
            expand=True,
            spacing=20,
            controls=[
                # Header
                ft.Container(
                    content=ft.Text(
                        "CV Analyzer App",
                        size=32,  # Increased from 28
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.INDIGO_800  # Changed from PRIMARY
                    ),
                    alignment=ft.alignment.center,
                    padding=20
                ),
                
                # Input section
                ft.Container(
                    content=ft.Column([
                        keywords_field,
                        ft.Row([
                            ft.Text(
                                "Search Algorithm:", 
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_800
                            ),
                        ]),
                        algorithm_radio,
                        ft.Row([
                            top_matches_dropdown,
                            ft.Container(expand=True),
                            progress_indicator,
                            search_button
                        ])
                    ]),
                    padding=20,
                    border_radius=16,  # Increased from 12
                    bgcolor=ft.Colors.WHITE,  # Changed from ON_SURFACE_VARIANT
                    border=ft.border.all(2, ft.Colors.GREY_200),  # Thicker border
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=4,
                        color=ft.Colors.GREY_300,
                        offset=ft.Offset(0, 2)
                    )
                ),
                
                # Summary section
                summary_section,
                
                # Results section
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            f"Search Results ({len(self.search_results)} found)",
                            size=20,  # Increased from 18
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_GREY_800
                        ) if self.search_results else ft.Text(
                            "No results to display",
                            color=ft.Colors.GREY_600
                        ),
                        ft.Divider(color=ft.Colors.GREY_300),
                        results_container if self.search_results else ft.Container()
                    ]),
                    expand=True,
                    padding=15,  # Increased from 10
                    border_radius=16,  # Increased from 12
                    bgcolor=ft.Colors.GREY_50,  # Changed from ON_SURFACE_VARIANT
                    border=ft.border.all(1, ft.Colors.GREY_200)
                )
            ]
        )
        
        return ft.View(
            "/search",
            [main_content],
            appbar=ft.AppBar(
                title=ft.Text("CV Analyzer"),
                bgcolor=ft.Colors.INDIGO_700,  # Changed from PRIMARY
                color=ft.Colors.WHITE
            ),
            bgcolor=ft.Colors.GREY_100  # Added background color
        )
    
    def build_summary_view(self, applicant_id: int) -> ft.View:
        """Membangun tampilan ringkasan pelamar"""
        # Cari data pelamar berdasarkan ID
        applicant = None
        for result in self.search_results:
            if result.id == applicant_id:
                applicant = result
                break
        
        if not applicant:
            # Jika tidak ditemukan, kembali ke pencarian
            self.page.go("/search")
            return self.build_search_view()
        
        # Load detail informasi pelamar (simulasi)
        self.load_applicant_details(applicant)
        
        # Buat konten ringkasan
        info_rows = [
            self.create_info_row("Name", applicant.name),
            self.create_info_row("Birth Date", applicant.birthdate),
            self.create_info_row("Address", applicant.address),
            self.create_info_row("Phone", applicant.phone),
            self.create_info_row("Email", applicant.email)
        ]
        
        # Skills section
        skills_section = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Skills", 
                    size=18,  # Increased from 16
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.INDIGO_800
                ),
                # PERBAIKAN: Mengganti ft.Wrap dengan ft.Row(wrap=True)
                ft.Row(
                    wrap=True,
                    controls=[
                        ft.Chip(
                            label=ft.Text(skill, color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.BLUE_600,
                            selected_color=ft.Colors.BLUE_700
                        ) for skill in (applicant.skills or ["Python", "Data Analysis", "Machine Learning"])
                    ],
                    spacing=8,
                    run_spacing=8
                )
            ]),
            padding=15,  # Increased from 10
            border_radius=12,
            bgcolor=ft.Colors.BLUE_50,
            border=ft.border.all(1, ft.Colors.BLUE_200)
        )
        
        # Job History section
        job_history_section = self.create_history_section(
            "Job History",
            applicant.job_history or [
                {"position": "Data Scientist", "company": "Tech Corp", "period": "2022-2024"},
                {"position": "Junior Analyst", "company": "Analytics Inc", "period": "2020-2022"}
            ],
            "position", "company", "period",
            ft.Colors.GREEN_50,  # Background color
            ft.Colors.GREEN_800  # Title color
        )
        
        # Education section
        education_section = self.create_history_section(
            "Education",
            applicant.education or [
                {"degree": "Master of Data Science", "institution": "University ABC", "period": "2018-2020"},
                {"degree": "Bachelor of Computer Science", "institution": "University XYZ", "period": "2014-2018"}
            ],
            "degree", "institution", "period",
            ft.Colors.PURPLE_50,  # Background color
            ft.Colors.PURPLE_800  # Title color
        )
        
        # View CV button
        view_cv_button = ft.ElevatedButton(
            text="View Full CV",
            icon=ft.Icons.PICTURE_AS_PDF_OUTLINED,
            on_click=lambda _: self.on_view_cv_click(applicant.cv_path),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.TEAL_600,  # Changed from PRIMARY
                color=ft.Colors.WHITE,
                elevation=6,
                shape=ft.StadiumBorder()
            )
        )
        
        main_content = ft.Column(
            expand=True,
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                # Personal Information
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Personal Information", 
                            size=22,  # Increased from 20
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_GREY_800
                        ),
                        ft.Divider(color=ft.Colors.GREY_300),
                        *info_rows
                    ]),
                    padding=20,
                    border_radius=16,  # Increased from 12
                    bgcolor=ft.Colors.WHITE,  # Changed from ON_SURFACE_VARIANT
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=4,
                        color=ft.Colors.GREY_300,
                        offset=ft.Offset(0, 2)
                    )
                ),
                
                # Skills
                skills_section,
                
                # Job History
                job_history_section,
                
                # Education
                education_section,
                
                # Action button
                ft.Container(
                    content=view_cv_button,
                    alignment=ft.alignment.center,
                    padding=20
                )
            ]
        )
        
        return ft.View(
            f"/summary/{applicant_id}",
            [main_content],
            appbar=ft.AppBar(
                title=ft.Text("Applicant Summary"),
                bgcolor=ft.Colors.INDIGO_700,  # Changed from PRIMARY
                color=ft.Colors.WHITE,
                leading=ft.IconButton(
                    ft.Icons.ARROW_BACK,
                    on_click=lambda _: self.page.go("/search"),
                    tooltip="Back to Search Results",
                    icon_color=ft.Colors.WHITE
                )
            ),
            bgcolor=ft.Colors.GREY_100  # Added background color
        )

    
    def create_info_row(self, label: str, value: str) -> ft.Row:
        """Helper untuk membuat baris informasi"""
        return ft.Row([
            ft.Container(
                content=ft.Text(
                    f"{label}:", 
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_800
                ),
                width=120
            ),
            ft.Text(
                value, 
                expand=True,
                color=ft.Colors.BLUE_GREY_600
            )
        ])
    
    def create_history_section(self, title: str, items: List[Dict], 
                             field1: str, field2: str, field3: str,
                             bg_color=ft.Colors.GREEN_50,
                             title_color=ft.Colors.GREEN_800) -> ft.Container:
        """Helper untuk membuat section riwayat"""
        history_items = []
        for item in items:
            history_items.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            item.get(field1, ""), 
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_GREY_800
                        ),
                        ft.Text(
                            item.get(field2, ""), 
                            color=ft.Colors.BLUE_GREY_600
                        ),
                        ft.Text(
                            item.get(field3, ""), 
                            size=12, 
                            color=ft.Colors.BLUE_GREY_500
                        )
                    ]),
                    padding=12,  # Increased from 10
                    margin=5,
                    border_radius=10,  # Increased from 8
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    shadow=ft.BoxShadow(
                        spread_radius=0.5,
                        blur_radius=2,
                        color=ft.Colors.GREY_200,
                        offset=ft.Offset(0, 1)
                    )
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    title, 
                    size=18,  # Increased from 16
                    weight=ft.FontWeight.BOLD,
                    color=title_color
                ),
                ft.Column(controls=history_items)
            ]),
            padding=15,  # Increased from 10
            border_radius=12,  # Increased from 8
            bgcolor=bg_color,
            border=ft.border.all(1, ft.Colors.GREY_200)
        )
    
    # Event Handlers
    def on_keywords_change(self, e):
        """Handler untuk perubahan kata kunci"""
        self.search_keywords = e.control.value
    
    def on_algorithm_change(self, e):
        """Handler untuk perubahan algoritma"""
        self.selected_algorithm = e.control.value
    
    def on_top_matches_change(self, e):
        """Handler untuk perubahan jumlah hasil teratas"""
        self.top_matches = e.control.value
    
    def on_search_click(self, e):
        """Handler untuk tombol pencarian"""
        if not self.search_keywords.strip():
            self.show_snackbar("Please enter search keywords")
            return
        
        self.perform_search()
    
    def on_summary_click(self, applicant_id: int):
        """Handler untuk tombol summary"""
        self.page.go(f"/summary/{applicant_id}")
    
    def on_view_cv_click(self, cv_path: str):
        """Handler untuk tombol view CV"""
        self.open_pdf_file(cv_path)
    
    # Core Methods (Integration Points)
    def perform_search(self):
        """
        Melakukan pencarian CV - INTEGRATION POINT untuk algoritma pencarian
        
        Di sini akan diintegrasikan:
        1. Algoritma KMP/Boyer-Moore untuk exact matching
        2. Levenshtein Distance untuk fuzzy matching
        3. Regex extraction untuk parsing CV
        4. Database queries untuk data pelamar
        """
        self.is_searching = True
        self.update_search_ui()
        
        try:
            # INTEGRATION POINT: Panggil fungsi pencarian dari modul lain
            # Contoh: from search_engine import perform_cv_search
            # results = perform_cv_search(
            #     keywords=self.search_keywords.split(','),
            #     algorithm=self.selected_algorithm,
            #     top_n=int(self.top_matches)
            # )
            
            # Simulasi hasil pencarian untuk demo
            self.simulate_search_results()
            
            # INTEGRATION POINT: Update waktu eksekusi dari hasil pencarian
            self.exact_match_time = "15ms"  # Dari hasil algoritma
            self.fuzzy_match_time = "45ms"  # Dari hasil algoritma
            
        except Exception as ex:
            self.show_snackbar(f"Search error: {str(ex)}")
        finally:
            self.is_searching = False
            self.update_search_ui()
    
    def simulate_search_results(self):
        """Simulasi hasil pencarian untuk demo"""
        # Data simulasi - dalam implementasi nyata, ini akan datang dari database
        sample_results = [
            ApplicantData(
                id=1,
                name="John Doe",
                cv_path="/path/to/cv1.pdf",
                email="john.doe@email.com",
                phone="+1234567890",
                address="123 Main St, City",
                birthdate="1990-01-15",
                matched_keywords={"Python": 5, "Data Science": 3, "Machine Learning": 2},
                total_matches=10
            ),
            ApplicantData(
                id=2,
                name="Jane Smith",
                cv_path="/path/to/cv2.pdf",
                email="jane.smith@email.com",
                phone="+1234567891",
                address="456 Oak Ave, Town",
                birthdate="1988-05-22",
                matched_keywords={"Python": 3, "React": 4, "JavaScript": 6},
                total_matches=13
            )
        ]
        
        # Filter berdasarkan kata kunci pencarian
        keywords = [k.strip().lower() for k in self.search_keywords.split(',')]
        filtered_results = []
        
        for result in sample_results:
            matched_keywords = {}
            total_matches = 0
            
            for keyword in keywords:
                for cv_keyword, count in result.matched_keywords.items():
                    if keyword in cv_keyword.lower():
                        matched_keywords[cv_keyword] = count
                        total_matches += count
            
            if matched_keywords:
                result.matched_keywords = matched_keywords
                result.total_matches = total_matches
                filtered_results.append(result)
        
        # Sort berdasarkan total matches
        filtered_results.sort(key=lambda x: x.total_matches, reverse=True)
        
        # Limit hasil sesuai top_matches
        self.search_results = filtered_results[:int(self.top_matches)]
    
    def load_applicant_details(self, applicant: ApplicantData):
        """
        Load detail informasi pelamar - INTEGRATION POINT untuk ekstraksi data
        
        Di sini akan diintegrasikan:
        1. Database queries untuk data lengkap pelamar
        2. Regex extraction untuk skills, job history, education dari CV
        3. PDF parsing untuk mendapatkan teks CV
        """
        # INTEGRATION POINT: Panggil fungsi ekstraksi dari modul lain
        # Contoh: from cv_extractor import extract_cv_info
        # extracted_data = extract_cv_info(applicant.cv_path)
        # applicant.skills = extracted_data.get('skills', [])
        # applicant.job_history = extracted_data.get('job_history', [])
        # applicant.education = extracted_data.get('education', [])
        
        # Simulasi data untuk demo
        if not applicant.skills:
            applicant.skills = ["Python", "Data Analysis", "Machine Learning", "SQL", "Statistics"]
        
        if not applicant.job_history:
            applicant.job_history = [
                {"position": "Senior Data Scientist", "company": "Tech Corp", "period": "2022-Present"},
                {"position": "Data Analyst", "company": "Analytics Inc", "period": "2020-2022"}
            ]
        
        if not applicant.education:
            applicant.education = [
                {"degree": "Master of Data Science", "institution": "University ABC", "period": "2018-2020"}
            ]
    
    def open_pdf_file(self, cv_path: str):
        """
        Membuka file PDF CV - INTEGRATION POINT untuk file handling
        """
        try:
            # INTEGRATION POINT: Validasi path file dari database
            # Dalam implementasi nyata, cv_path akan berisi path yang valid
            
            if not os.path.exists(cv_path):
                self.show_snackbar("CV file not found")
                return
            
            # Buka file berdasarkan sistem operasi
            system = platform.system()
            if system == "Windows":
                os.startfile(cv_path)
            elif system == "Darwin":  # macOS
                subprocess.call(["open", cv_path])
            elif system == "Linux":
                subprocess.call(["xdg-open", cv_path])
            else:
                self.show_snackbar("Cannot open PDF on this system")
                
        except Exception as ex:
            self.show_snackbar(f"Error opening CV: {str(ex)}")
    
    # UI Helper Methods
    def update_search_ui(self):
        """Update UI berdasarkan status pencarian"""
        self.page.go("/search")  # Refresh view
    
    def show_snackbar(self, message: str):
        """Menampilkan snackbar dengan pesan"""
        snackbar = ft.SnackBar(
            content=ft.Text(message),
            action="OK"
        )
        self.page.snack_bar = snackbar
        snackbar.open = True
        self.page.update()

# Fungsi utama untuk menjalankan aplikasi
def main(page: ft.Page):
    """Entry point aplikasi"""
    app = ATSApp(page)

if __name__ == "__main__":
    ft.app(target=main)