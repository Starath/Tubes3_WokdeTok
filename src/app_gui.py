import flet as ft
import os
import subprocess
import platform
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio
import time

from algorithm.KMP import kmp_search

# (Tambahkan di bawah imports)
# Dummy CV Database (menggantikan data simulasi yang ada)
DUMMY_CV_DATABASE = [
    {
        "id": 1,
        "name": "Farrell Jabaar",
        "cv_path": "/path/to/farrell_cv.pdf",
        "email": "farrell.j@email.com", "phone": "081234567890", "address": "Bandung, Indonesia", "birthdate": "2003-05-10",
        "cv_text": """
        Farrell Jabaar - Data Scientist
        Summary: Experienced in Python, SQL, and machine learning.
        Skills: Python, TensorFlow, PyTorch, SQL, NoSQL, Data Visualization.
        Experience:
        - Data Scientist at Tech Corp (2022-Present). Developed machine learning models.
        - Junior Analyst at Data Inc (2020-2022). Focused on data cleaning with Python.
        """
    },
    {
        "id": 2,
        "name": "Aramazaya",
        "cv_path": "/path/to/aramazaya_cv.pdf",
        "email": "aramazaya.a@email.com", "phone": "081234567891", "address": "Jakarta, Indonesia", "birthdate": "2004-01-15",
        "cv_text": """
        Aramazaya - Full-Stack Developer
        Summary: Proficient in React and Node.js, with a strong background in web development.
        Skills: JavaScript, React, Node.js, Express, MongoDB, HTML, CSS.
        Experience:
        - Frontend Developer at Web Solutions (2021-Present). Building responsive UIs with React.
        - Intern at Creative Agency (2020). Worked on various web projects.
        """
    },
    {
        "id": 3,
        "name": "Athian Nugraha",
        "cv_path": "/path/to/athian_cv.pdf",
        "email": "athian.n@email.com", "phone": "081234567892", "address": "Surabaya, Indonesia", "birthdate": "2004-08-20",
        "cv_text": """
        Athian Nugraha - DevOps Engineer
        Summary: Skilled in cloud infrastructure and automation using Python and Docker.
        Skills: Python, Docker, Kubernetes, AWS, CI/CD, Terraform, SQL.
        Experience:
        - DevOps Engineer at Cloudify (2022-Present). Managing deployments and CI/CD pipelines.
        - System Administrator at HostNet (2020-2022). Maintained server infrastructure.
        """
    }
]

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

# Kontrol Kustom untuk Kartu CV - Redesigned untuk lebih compact
class CVCard(ft.Card):
    def __init__(self, applicant_data: ApplicantData, on_summary_click, on_view_cv_click):
        super().__init__()
        self.applicant_data = applicant_data
        self.on_summary_click = on_summary_click
        self.on_view_cv_click = on_view_cv_click
        
        # Styling kartu - lebih compact
        self.elevation = 2
        self.margin = ft.margin.only(bottom=8)
        
        # Buat konten kartu
        self._build_content()
    
    def _build_content(self):
        # Buat keyword chips yang lebih compact
        keyword_chips = []
        for keyword, count in self.applicant_data.matched_keywords.items():
            keyword_chips.append(
                ft.Container(
                    content=ft.Text(
                        f"{keyword} ({count})",
                        size=11,
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.W_500
                    ),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=ft.Colors.BLUE_600,
                    border_radius=12,
                    margin=ft.margin.only(right=4, bottom=4)
                )
            )
        
        # Tombol aksi - lebih kecil
        action_buttons = ft.Row(
            controls=[
                ft.TextButton(
                    text="Summary",
                    icon=ft.Icons.INFO_OUTLINE,
                    on_click=lambda _: self.on_summary_click(self.applicant_data.id),
                    style=ft.ButtonStyle(
                        color=ft.Colors.INDIGO_700,
                        padding=ft.padding.symmetric(horizontal=12, vertical=8)
                    )
                ),
                ft.TextButton(
                    text="View CV",
                    icon=ft.Icons.VISIBILITY_OUTLINED,
                    on_click=lambda _: self.on_view_cv_click(self.applicant_data.cv_path),
                    style=ft.ButtonStyle(
                        color=ft.Colors.TEAL_700,
                        padding=ft.padding.symmetric(horizontal=12, vertical=8)
                    )
                )
            ],
            alignment=ft.MainAxisAlignment.END,
            spacing=8
        )
        
        # Konten utama kartu - lebih compact
        self.content = ft.Container(
            padding=12,
            content=ft.Column(
                spacing=6,
                tight=True,
                controls=[
                    # Header row dengan nama dan total matches
                    ft.Row(
                        controls=[
                            ft.Text(
                                self.applicant_data.name,
                                weight=ft.FontWeight.BOLD,
                                size=16,
                                color=ft.Colors.GREY_900,
                                expand=True
                            ),
                            ft.Container(
                                content=ft.Text(
                                    f"{self.applicant_data.total_matches} matches",
                                    size=12,
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.W_600
                                ),
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                bgcolor=ft.Colors.GREEN_600,
                                border_radius=10
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    
                    # Keywords dalam format wrap
                    ft.Container(
                        content=ft.Row(
                            wrap=True,
                            controls=keyword_chips,
                            spacing=0,
                            run_spacing=0
                        ),
                        margin=ft.margin.only(top=4, bottom=4)
                    ),
                    
                    # Action buttons
                    action_buttons
                ]
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
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
        self.page.padding = 0  # Remove default padding
        
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
        """Membangun tampilan pencarian utama - Redesigned untuk efisiensi ruang"""
        
        # Input section - lebih compact
        input_section = ft.Container(
            content=ft.Column([
                # Keywords input
                ft.TextField(
                    label="Search Keywords",
                    hint_text="e.g., Python, React, SQL",
                    value=self.search_keywords,
                    on_change=self.on_keywords_change,
                    on_submit=self.on_search_click,
                    border_color=ft.Colors.BLUE_400,
                    focused_border_color=ft.Colors.BLUE_600,
                    dense=True,
                    height=50
                ),
                
                # Controls row - algorithm, top matches, and search button
                ft.Row([
                    # Algorithm selection
                    ft.Container(
                        content=ft.RadioGroup(
                            content=ft.Row([
                                ft.Radio(value="KMP", label="KMP", active_color=ft.Colors.PURPLE_600),
                                ft.Radio(value="BM", label="BM", active_color=ft.Colors.PURPLE_600),
                                ft.Radio(value="AC", label="AC", active_color=ft.Colors.PURPLE_600)
                            ], tight=True),
                            value=self.selected_algorithm,
                            on_change=self.on_algorithm_change
                        ),
                        expand=True
                    ),
                    
                    # Top matches dropdown
                    ft.Dropdown(
                        label="Top",
                        options=[
                            ft.dropdown.Option("5"),
                            ft.dropdown.Option("10"),
                            ft.dropdown.Option("20"),
                            ft.dropdown.Option("50")
                        ],
                        value=self.top_matches,
                        width=80,
                        on_change=self.on_top_matches_change,
                        dense=True,
                    ),
                    
                    # Search button with progress indicator
                    ft.Container(
                        content=ft.Stack([
                            ft.ElevatedButton(
                                text="Search",
                                icon=ft.Icons.SEARCH,
                                on_click=self.on_search_click,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.BLUE_600,
                                    color=ft.Colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=8)
                                ),
                                disabled=self.is_searching,
                                height=50,
                                width=100
                            ),
                            ft.ProgressRing(
                                visible=self.is_searching,
                                width=20,
                                height=20,
                                color=ft.Colors.BLUE_600
                            )
                        ]),
                        alignment=ft.alignment.center
                    )
                ], spacing=12)
            ], spacing=8, tight=True),
            padding=12,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300),
            margin=ft.margin.only(bottom=8)
        )
        
        # Results summary - very compact
        results_summary = ft.Container(
            content=ft.Row([
                ft.Text(
                    f"Results: {len(self.search_results)} found",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_800
                ),
                ft.Container(expand=True),
                ft.Text(
                    f"Time: {self.exact_match_time}" if self.exact_match_time else "",
                    size=12,
                    color=ft.Colors.GREEN_700
                ),
            ], tight=True),
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=6,
            visible=bool(self.search_results or self.exact_match_time),
            margin=ft.margin.only(bottom=8)
        )
        
        # Results ListView - This is the main focus area
        if self.search_results:
            results_content = ft.ListView(
                controls=[CVCard(result, self.on_summary_click, self.on_view_cv_click) 
                         for result in self.search_results],
                spacing=0,
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                expand=True,
                auto_scroll=False
            )
        else:
            results_content = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SEARCH_OFF, size=48, color=ft.Colors.GREY_400),
                    ft.Text(
                        "No results yet",
                        size=16,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "Enter keywords and click Search to find matching CVs",
                        size=12,
                        color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER
                    )
                ], 
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True),
                alignment=ft.alignment.center,
                expand=True
            )
        
        # Main layout - maximizing space for results
        main_content = ft.Column(
            controls=[
                # Compact header
                ft.Container(
                    content=ft.Text(
                        "CV Analyzer",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE
                    ),
                    alignment=ft.alignment.center,
                    padding=ft.padding.symmetric(vertical=12),
                    bgcolor=ft.Colors.INDIGO_700,
                    border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8)
                ),
                
                # Content area
                ft.Container(
                    content=ft.Column([
                        input_section,
                        results_summary,
                        # Results area - this takes most of the space
                        ft.Container(
                            content=results_content,
                            expand=True,
                            bgcolor=ft.Colors.GREY_50,
                            border_radius=8,
                            border=ft.border.all(1, ft.Colors.GREY_200)
                        )
                    ], 
                    spacing=0,
                    expand=True),
                    padding=12,
                    expand=True
                )
            ],
            spacing=0,
            expand=True
        )
        
        return ft.View(
            "/search",
            [main_content],
            bgcolor=ft.Colors.GREY_100,
            padding=0
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
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.INDIGO_800
                ),
                ft.Row(
                    wrap=True,
                    controls=[
                        ft.Chip(
                            label=ft.Text(skill, color=ft.Colors.BLACK),
                            bgcolor=ft.Colors.BLUE_600,
                            selected_color=ft.Colors.BLUE_700
                        ) for skill in (applicant.skills or ["Python", "Data Analysis", "Machine Learning"])
                    ],
                    spacing=8,
                    run_spacing=8
                )
            ]),
            padding=15,
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
            ft.Colors.GREEN_50,
            ft.Colors.GREEN_800
        )
        
        # Education section
        education_section = self.create_history_section(
            "Education",
            applicant.education or [
                {"degree": "Master of Data Science", "institution": "University ABC", "period": "2018-2020"},
                {"degree": "Bachelor of Computer Science", "institution": "University XYZ", "period": "2014-2018"}
            ],
            "degree", "institution", "period",
            ft.Colors.PURPLE_50,
            ft.Colors.PURPLE_800
        )
        
        # View CV button
        view_cv_button = ft.ElevatedButton(
            text="View Full CV",
            icon=ft.Icons.PICTURE_AS_PDF_OUTLINED,
            on_click=lambda _: self.on_view_cv_click(applicant.cv_path),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.TEAL_600,
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
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_GREY_800
                        ),
                        ft.Divider(color=ft.Colors.GREY_300),
                        *info_rows
                    ]),
                    padding=20,
                    border_radius=16,
                    bgcolor=ft.Colors.WHITE,
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
                bgcolor=ft.Colors.INDIGO_700,
                color=ft.Colors.WHITE,
                leading=ft.IconButton(
                    ft.Icons.ARROW_BACK,
                    on_click=lambda _: self.page.go("/search"),
                    tooltip="Back to Search Results",
                    icon_color=ft.Colors.WHITE
                )
            ),
            bgcolor=ft.Colors.GREY_100
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
                    padding=12,
                    margin=5,
                    border_radius=10,
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
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=title_color
                ),
                ft.Column(controls=history_items)
            ]),
            padding=15,
            border_radius=12,
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
        """
        self.is_searching = True
        self.update_search_ui()
        
        self.page.update()
        time.sleep(0.1)

        found_applicants = []
        
        start_time = time.perf_counter()
        
        try:
            keywords = [k.strip().lower() for k in self.search_keywords.split(',') if k.strip()]

            # Lakukan Pencarian dengan KMP
            if self.selected_algorithm == "KMP":
                for applicant_data in DUMMY_CV_DATABASE:
                    cv_text_lower = applicant_data["cv_text"].lower()
                    
                    matched_keywords_details = {}
                    total_matches_count = 0
                    
                    for keyword in keywords:
                        matches = kmp_search(cv_text_lower, keyword)
                        if matches:
                            count = len(matches)
                            matched_keywords_details[keyword.capitalize()] = count
                            total_matches_count += count
                    
                    if total_matches_count > 0:
                        new_applicant = ApplicantData(
                            id=applicant_data["id"],
                            name=applicant_data["name"],
                            cv_path=applicant_data["cv_path"],
                            email=applicant_data["email"],
                            phone=applicant_data["phone"],
                            address=applicant_data["address"],
                            birthdate=applicant_data["birthdate"],
                            matched_keywords=matched_keywords_details,
                            total_matches=total_matches_count
                        )
                        found_applicants.append(new_applicant)

            # Urutkan hasil berdasarkan total match terbanyak
            found_applicants.sort(key=lambda x: x.total_matches, reverse=True)
            
            # Ambil hasil sesuai 'top_matches' dan simpan
            self.search_results = found_applicants[:int(self.top_matches)]

            # Hentikan timer dan format waktu eksekusi
            end_time = time.perf_counter()
            execution_time_ms = (end_time - start_time) * 1000
            self.exact_match_time = f"{execution_time_ms:.2f} ms"
            self.fuzzy_match_time = "N/A"

        except Exception as ex:
            self.show_snackbar(f"Search error: {str(ex)}")
        finally:
            self.is_searching = False
            self.update_search_ui()
            self.page.update()
    
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
        try:
            if hasattr(self.page, 'views') and self.page.views:
                current_view = self.page.views[-1]
                if current_view.route == "/search":
                    # Refresh search view dengan hasil terbaru
                    self.page.views[-1] = self.build_search_view()
            self.page.update()
        except Exception as e:
            print(f"UI update error: {e}")
            self.page.update()
    
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