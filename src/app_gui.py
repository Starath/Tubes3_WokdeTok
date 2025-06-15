import flet as ft
import os
import subprocess
import platform
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio
import time

from algorithm.KMP import kmp_search
from algorithm.boyer_moore import bm_search
from algorithm.aho_corasick import AhoCorasick
from algorithm.levenshtein import levenshtein_search
from cv_extractor import extract_info_from_text


LEVENSHTEIN_THRESHOLD = 2

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
        """Initializes all views."""
        pass
    
    def route_change(self, route):
        """Handler for route changes."""
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
        """Handler for view pop (back button)."""
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)
    
    def build_search_view(self) -> ft.View:
        """Builds the main search view - Redesigned for space efficiency."""
        
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
                                ft.Radio(value="KMP", label="Knuth-Morris-Pratt", active_color=ft.Colors.PURPLE_600),
                                ft.Radio(value="BM", label="Boyer-Moore", active_color=ft.Colors.PURPLE_600),
                                ft.Radio(value="AC", label="Aho-Corasick", active_color=ft.Colors.PURPLE_600)
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
                        width=85,
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
                        f"Exact Match: {self.exact_match_time}" if self.exact_match_time else "",
                        size=12,
                        color=ft.Colors.GREEN_700,
                        visible=bool(self.exact_match_time)
                    ),
                    ft.Text(
                        f"Fuzzy Match: {self.fuzzy_match_time}" if self.fuzzy_match_time else "",
                        size=12,
                        color=ft.Colors.ORANGE_800,
                        visible=bool(self.fuzzy_match_time)
                    ),
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.END)
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
        """Builds the applicant summary view."""
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
        # NOTE: ONLY FOR SIMULATION
        self.load_applicant_details(applicant)
        # TODO: Use real CV
        summary_section = ft.Container(
            content=ft.Column([
                ft.Text("Summary", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_800),
                ft.Text(applicant.summary, color=ft.Colors.BLUE_GREY_700, size=14)
            ]),
            padding=15,
            border_radius=12,
            bgcolor=ft.Colors.INDIGO_50,
            border=ft.border.all(1, ft.Colors.INDIGO_200)
        )

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
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
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
                
                summary_section,
                
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
        """Helper to create an information row."""
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
        """Helper to create a history section."""
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
        """Handler for keyword changes."""
        self.search_keywords = e.control.value
    
    def on_algorithm_change(self, e):
        """Handler for algorithm changes."""
        self.selected_algorithm = e.control.value
    
    def on_top_matches_change(self, e):
        """Handler for changing the number of top matches."""
        self.top_matches = e.control.value
    
    def on_search_click(self, e):
        """Handler for the search button click."""
        if not self.search_keywords.strip():
            self.show_snackbar("Please enter search keywords")
            return
        
        self.perform_search()
    
    def on_summary_click(self, applicant_id: int):
        """Handler for the summary button click."""
        self.page.go(f"/summary/{applicant_id}")
    
    def on_view_cv_click(self, cv_path: str):
        """Handler for the view CV button click."""
        self.open_pdf_file(cv_path)
    
    # Core Methods (Integration Points)
    def perform_search(self):
        """
        Performs a CV search in two stages: Exact Match then Fuzzy Match.
        """
        self.is_searching = True
        self.exact_match_time = ""
        self.fuzzy_match_time = ""
        self.update_search_ui()
        self.page.update()
        time.sleep(0.1) # Jeda singkat untuk UI update

        # Using dictionary for easier update
        found_applicants_map: Dict[int, ApplicantData] = {}
        
        try:
            keywords = [k.strip().lower() for k in self.search_keywords.split(',') if k.strip()]
            if not keywords:
                self.show_snackbar("Keywords cannot be empty.")
                return

            # Exact Match (KMP, BM, Aho-Corasick)
            start_exact_time = time.perf_counter()
            found_keywords_exact = set()

            search_function = None
            if self.selected_algorithm == "KMP":
                search_function = kmp_search
            elif self.selected_algorithm == "BM":
                search_function = bm_search
            
            # Aho-Corasick handled separately  
            if self.selected_algorithm == "AC":
                ac_automaton = AhoCorasick(keywords)
                for applicant_data in DUMMY_CV_DATABASE:
                    cv_text_lower = applicant_data["cv_text"].lower()
                    matches = ac_automaton.search(cv_text_lower)
                    
                    if matches:
                        total_matches_count = 0
                        matched_keywords_details = {}
                        for keyword, indices in matches.items():
                            count = len(indices)
                            matched_keywords_details[keyword.capitalize()] = count
                            total_matches_count += count
                            found_keywords_exact.add(keyword)
                        
                        if applicant_data["id"] not in found_applicants_map:
                             found_applicants_map[applicant_data["id"]] = ApplicantData(id=applicant_data["id"], name=applicant_data["name"], cv_path=applicant_data["cv_path"], email=applicant_data["email"], phone=applicant_data["phone"], address=applicant_data["address"], birthdate=applicant_data["birthdate"], matched_keywords={}, total_matches=0)
                        found_applicants_map[applicant_data["id"]].matched_keywords.update(matched_keywords_details)
                        found_applicants_map[applicant_data["id"]].total_matches += total_matches_count
            else: # KMP or BM
                for applicant_data in DUMMY_CV_DATABASE:
                    cv_text_lower = applicant_data["cv_text"].lower()
                    for keyword in keywords:
                        matches = search_function(cv_text_lower, keyword)
                        if matches:
                            count = len(matches)
                            found_keywords_exact.add(keyword)
                            
                            if applicant_data["id"] not in found_applicants_map:
                                found_applicants_map[applicant_data["id"]] = ApplicantData(id=applicant_data["id"], name=applicant_data["name"], cv_path=applicant_data["cv_path"], email=applicant_data["email"], phone=applicant_data["phone"], address=applicant_data["address"], birthdate=applicant_data["birthdate"], matched_keywords={}, total_matches=0)
                            
                            # Update detail keyword
                            applicant = found_applicants_map[applicant_data["id"]]
                            applicant.matched_keywords[keyword.capitalize()] = applicant.matched_keywords.get(keyword.capitalize(), 0) + count
                            applicant.total_matches += count

            end_exact_time = time.perf_counter()
            self.exact_match_time = f"{(end_exact_time - start_exact_time) * 1000:.2f} ms"

            # Fuzzy Match (Levenshtein) for unfounded keyword
            unfound_keywords = [k for k in keywords if k not in found_keywords_exact]
            if unfound_keywords:
                start_fuzzy_time = time.perf_counter()
                
                for applicant_data in DUMMY_CV_DATABASE:
                    cv_text_lower = applicant_data["cv_text"].lower()
                    for keyword in unfound_keywords:
                        # Gunakan levenshtein_search
                        matches = levenshtein_search(cv_text_lower, keyword, LEVENSHTEIN_THRESHOLD)
                        if matches:
                            count = len(matches)
                            
                            if applicant_data["id"] not in found_applicants_map:
                                found_applicants_map[applicant_data["id"]] = ApplicantData(id=applicant_data["id"], name=applicant_data["name"], cv_path=applicant_data["cv_path"], email=applicant_data["email"], phone=applicant_data["phone"], address=applicant_data["address"], birthdate=applicant_data["birthdate"], matched_keywords={}, total_matches=0)
                            
                            applicant = found_applicants_map[applicant_data["id"]]
                            fuzzy_keyword_label = f"{keyword.capitalize()} (fuzzy)"
                            applicant.matched_keywords[fuzzy_keyword_label] = applicant.matched_keywords.get(fuzzy_keyword_label, 0) + count
                            applicant.total_matches += count
                
                end_fuzzy_time = time.perf_counter()
                self.fuzzy_match_time = f"{(end_fuzzy_time - start_fuzzy_time) * 1000:.2f} ms"
            else:
                 self.fuzzy_match_time = "N/A (all found)"


            # Finalization
            final_results = list(found_applicants_map.values())
            final_results.sort(key=lambda x: x.total_matches, reverse=True)
            self.search_results = final_results[:int(self.top_matches)]

        except Exception as ex:
            self.show_snackbar(f"Search error: {str(ex)}")
        finally:
            self.is_searching = False
            self.update_search_ui()
    
    def load_applicant_details(self, applicant: ApplicantData):
        """
        Loads detailed applicant information - INTEGRATION POINT for data extraction
        
        TODO:
        1. Database queries for complete applicant data
        2. Regex extraction for skills, job history, education from CV
        3. PDF parsing to get CV text
        """

        dummy_record = next((item for item in DUMMY_CV_DATABASE if item["id"] == applicant.id), None)

        if not dummy_record:
            applicant.summary = "Applicant data not found."
            applicant.skills = []
            applicant.job_history = []
            applicant.education = []
            return

        # Get CV Text
        cv_text = dummy_record.get("cv_text", "")

        extracted_data = extract_info_from_text(cv_text)
        
        # Update the applicant data
        applicant.summary = extracted_data.get("summary", "Summary cant be extracted.")
        applicant.skills = extracted_data.get("skills", [])
        applicant.job_history = extracted_data.get("experience", [])
        applicant.education = extracted_data.get("education", [])
    
    def open_pdf_file(self, cv_path: str):
        """
        Opens the CV PDF file - INTEGRATION POINT for file handling
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
        """Updates the UI based on the search status."""
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
        """Displays a snackbar with a message."""
        snackbar = ft.SnackBar(
            content=ft.Text(message),
            action="OK"
        )
        self.page.snack_bar = snackbar
        snackbar.open = True
        self.page.update()

# Fungsi utama untuk menjalankan aplikasi
def main(page: ft.Page):
    """Application entry point."""
    app = ATSApp(page)

if __name__ == "__main__":
    ft.app(target=main)
