import customtkinter as ctk
from tkinter import messagebox


class ModernInstalockConfigurator:
    """Configurador moderno de Instalock com sistema de abas ultra clean"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.colors = app.colors
        
        # Estado das abas
        self.current_tab = 0  # 0 = 1st Pick, 1 = 2nd Pick, 2 = 3rd Pick
        
        # Valores dos picks
        self.pick_values = {
            0: app.instalock_champion or "",
            1: app.instalock_backup_2 or "",
            2: app.instalock_backup_3 or ""
        }
        
        self.create_window()
    
    def create_window(self):
        """Cria janela modal ultra moderna"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("⚡ Instalock Configuration")
        self.dialog.geometry("800x750")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centralizar
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 300
        y = (self.dialog.winfo_screenheight() // 2) - 225
        self.dialog.geometry(f"800x750+{x}+{y}")
        
        self.dialog.configure(fg_color=self.colors['bg_dark'])
        
        # Container principal
        main = ctk.CTkFrame(self.dialog, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main)
        
        # Sistema de abas
        self.create_tabs(main)
        
        # Área de conteúdo
        self.create_content_area(main)
        
        # Footer com botões
        self.create_footer(main)
        
        # Mostrar primeira aba
        self.show_tab(0)
    
    def create_header(self, parent):
        """Header moderno com título e subtítulo"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        # Ícone + Título
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="⚡",
            font=("Segoe UI Emoji", 32),
            text_color=self.colors['primary']
        ).pack(side="left", padx=(0, 10))
        
        text_container = ctk.CTkFrame(title_frame, fg_color="transparent")
        text_container.pack(side="left", fill="both")
        
        ctk.CTkLabel(
            text_container,
            text="Instalock Configuration",
            font=("Consolas", 18, "bold"),
            text_color=self.colors['primary'],
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            text_container,
            text="Configure your champion picks with backup system",
            font=("Consolas", 9),
            text_color=self.colors['text_secondary'],
            anchor="w"
        ).pack(anchor="w")
    
    def create_tabs(self, parent):
        """Sistema de abas moderno e clean"""
        tabs_container = ctk.CTkFrame(
            parent,
            fg_color=self.colors['bg_medium'],
            corner_radius=12,
            height=70
        )
        tabs_container.pack(fill="x", pady=(0, 15))
        tabs_container.pack_propagate(False)
        
        tabs_inner = ctk.CTkFrame(tabs_container, fg_color="transparent")
        tabs_inner.pack(fill="both", expand=True, padx=8, pady=8)
        
        self.tab_buttons = []
        
        # Configuração das abas
        tab_configs = [
            {
                'icon': '🎯',
                'title': '1st Pick',
                'subtitle': 'Main Champion',
                'color': self.colors['success'],
                'index': 0
            },
            {
                'icon': '🔄',
                'title': '2nd Pick',
                'subtitle': 'First Backup',
                'color': self.colors['warning'],
                'index': 1
            },
            {
                'icon': '🔄',
                'title': '3rd Pick',
                'subtitle': 'Second Backup',
                'color': self.colors['danger'],
                'index': 2
            }
        ]
        
        for config in tab_configs:
            tab = self.create_tab_button(tabs_inner, config)
            tab.pack(side="left", fill="both", expand=True, padx=4)
            self.tab_buttons.append(tab)
    
    def create_tab_button(self, parent, config):
        """Cria botão de aba individual"""
        tab = ctk.CTkFrame(
            parent,
            fg_color=self.colors['bg_light'],
            corner_radius=10,
            cursor="hand2"
        )
        
        # Armazenar dados
        tab._index = config['index']
        tab._color = config['color']
        tab._is_active = False
        
        # Container interno
        content = ctk.CTkFrame(tab, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=12, pady=10)
        
        # Linha superior: ícone + título
        top_line = ctk.CTkFrame(content, fg_color="transparent")
        top_line.pack(fill="x")
        
        icon = ctk.CTkLabel(
            top_line,
            text=config['icon'],
            font=("Segoe UI Emoji", 20),
            text_color=config['color']
        )
        icon.pack(side="left", padx=(0, 8))
        
        title = ctk.CTkLabel(
            top_line,
            text=config['title'],
            font=("Consolas", 13, "bold"),
            text_color=self.colors['text_primary'],
            anchor="w"
        )
        title.pack(side="left", fill="x", expand=True)
        
        # Linha inferior: subtítulo
        subtitle = ctk.CTkLabel(
            content,
            text=config['subtitle'],
            font=("Consolas", 9),
            text_color=self.colors['text_secondary'],
            anchor="w"
        )
        subtitle.pack(anchor="w", pady=(2, 0))
        
        # Indicador de preenchimento
        indicator = ctk.CTkFrame(
            content,
            fg_color="transparent",
            height=3
        )
        indicator.pack(fill="x", pady=(4, 0))
        
        indicator_bar = ctk.CTkFrame(
            indicator,
            fg_color=config['color'],
            height=3,
            corner_radius=2
        )
        
        tab._indicator_bar = indicator_bar
        tab._icon = icon
        tab._title = title
        tab._subtitle = subtitle
        
        # Binds
        def on_click(e):
            self.show_tab(config['index'])
        
        def on_hover(e):
            if not tab._is_active:
                tab.configure(fg_color=self.colors['bg_card'])
        
        def on_leave(e):
            if not tab._is_active:
                tab.configure(fg_color=self.colors['bg_light'])
        
        for widget in [tab, content, top_line, icon, title, subtitle]:
            widget.bind("<Button-1>", on_click)
        
        tab.bind("<Enter>", on_hover)
        tab.bind("<Leave>", on_leave)
        
        # Atualizar indicador baseado no valor
        self.update_tab_indicator(tab, config['index'])
        
        return tab
    
    def update_tab_indicator(self, tab, index):
        """Atualiza indicador visual da aba"""
        value = self.pick_values[index].strip()
        
        if value:
            # Mostrar barra preenchida
            tab._indicator_bar.pack(fill="x")
        else:
            # Esconder barra
            tab._indicator_bar.pack_forget()
    
    def show_tab(self, index):
        """Mostra aba específica"""
        self.current_tab = index
        
        # Atualizar visual das abas
        for i, tab in enumerate(self.tab_buttons):
            if i == index:
                # Aba ativa
                tab._is_active = True
                tab.configure(
                    fg_color=self.colors['bg_card'],
                    border_width=2,
                    border_color=tab._color
                )
                tab._title.configure(text_color=tab._color)
            else:
                # Aba inativa
                tab._is_active = False
                tab.configure(
                    fg_color=self.colors['bg_light'],
                    border_width=0
                )
                tab._title.configure(text_color=self.colors['text_primary'])
        
        # Atualizar conteúdo
        self.update_content()
    
    def create_content_area(self, parent):
        """Área de conteúdo para entrada do campeão"""
        self.content_frame = ctk.CTkFrame(
            parent,
            fg_color=self.colors['bg_card'],
            corner_radius=12,
            border_width=2,
            border_color=self.colors['primary']
        )
        self.content_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Será preenchido dinamicamente
        self.content_widgets = {}
    
    def update_content(self):
        """Atualiza conteúdo baseado na aba atual"""
        # Limpar conteúdo anterior
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Container interno
        content = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Configurações da aba atual
        configs = [
            {
                'icon': '🎯',
                'title': '1st Pick - Main Champion',
                'desc': 'Your primary champion choice. This will be picked first.',
                'placeholder': 'Enter champion name (e.g., Yasuo, Zed, Random)',
                'color': self.colors['success']
            },
            {
                'icon': '🔄',
                'title': '2nd Pick - First Backup',
                'desc': 'Backup champion if your 1st pick is banned.',
                'placeholder': 'Enter backup champion (optional)',
                'color': self.colors['warning']
            },
            {
                'icon': '🔄',
                'title': '3rd Pick - Second Backup',
                'desc': 'Final backup if both 1st and 2nd are banned.',
                'placeholder': 'Enter final backup (optional)',
                'color': self.colors['danger']
            }
        ]
        
        config = configs[self.current_tab]
        
        # Header da aba
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header,
            text=config['icon'],
            font=("Segoe UI Emoji", 28),
            text_color=config['color']
        ).pack(side="left", padx=(0, 12))
        
        text_frame = ctk.CTkFrame(header, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True)
        
        ctk.CTkLabel(
            text_frame,
            text=config['title'],
            font=("Consolas", 14, "bold"),
            text_color=config['color'],
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            text_frame,
            text=config['desc'],
            font=("Consolas", 9),
            text_color=self.colors['text_secondary'],
            anchor="w",
            wraplength=400
        ).pack(anchor="w", pady=(2, 0))
        
        # Campo de entrada
        entry_frame = ctk.CTkFrame(content, fg_color="transparent")
        entry_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(
            entry_frame,
            text="Champion Name:",
            font=("Consolas", 11, "bold"),
            text_color=self.colors['text_primary']
        ).pack(anchor="w", pady=(0, 8))
        
        entry = ctk.CTkEntry(
            entry_frame,
            placeholder_text=config['placeholder'],
            height=45,
            font=("Consolas", 12),
            fg_color=self.colors['bg_light'],
            border_color=config['color'],
            border_width=2,
            text_color=self.colors['text_primary']
        )
        entry.pack(fill="x")
        entry.insert(0, self.pick_values[self.current_tab])
        
        # Auto-focus
        entry.focus_set()
        
        # Bind para salvar ao trocar de aba
        def on_change(e):
            self.pick_values[self.current_tab] = entry.get().strip()
            self.update_tab_indicator(self.tab_buttons[self.current_tab], self.current_tab)
        
        entry.bind("<KeyRelease>", on_change)
        
        self.content_widgets['entry'] = entry
        
        # Dicas
        if self.current_tab == 0:
            tips_frame = ctk.CTkFrame(
                content,
                fg_color=self.colors['bg_light'],
                corner_radius=8
            )
            tips_frame.pack(fill="x", pady=(15, 0))
            
            tips_content = ctk.CTkFrame(tips_frame, fg_color="transparent")
            tips_content.pack(fill="x", padx=15, pady=12)
            
            ctk.CTkLabel(
                tips_content,
                text="💡 Tips:",
                font=("Consolas", 10, "bold"),
                text_color=self.colors['info']
            ).pack(anchor="w")
            
            tips = [
                "• Type 'Random' for random champion selection",
                "• 1st Pick is required, backups are optional",
                "• If all champions are banned, you must pick manually."
            ]
            
            for tip in tips:
                ctk.CTkLabel(
                    tips_content,
                    text=tip,
                    font=("Consolas", 9),
                    text_color=self.colors['text_secondary'],
                    anchor="w"
                ).pack(anchor="w", pady=1)
    
    def create_footer(self, parent):
        """Footer com botões de ação"""
        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.pack(fill="x")
        
        # Botão Clear (esquerda)
        clear_btn = ctk.CTkButton(
            footer,
            text="🗑️ Clear Current",
            height=40,
            width=130,
            font=("Consolas", 11, "bold"),
            fg_color=self.colors['bg_light'],
            hover_color=self.colors['danger'],
            text_color=self.colors['text_primary'],
            corner_radius=8,
            command=self.clear_current
        )
        clear_btn.pack(side="left")
        
        # Espaçador
        ctk.CTkFrame(footer, fg_color="transparent").pack(side="left", expand=True)
        
        # Botão Cancel
        cancel_btn = ctk.CTkButton(
            footer,
            text="✖ Cancel",
            height=40,
            width=110,
            font=("Consolas", 11, "bold"),
            fg_color=self.colors['bg_light'],
            hover_color=self.colors['bg_medium'],
            text_color=self.colors['text_primary'],
            corner_radius=8,
            command=self.cancel
        )
        cancel_btn.pack(side="right", padx=(8, 0))
        
        # Botão Save
        save_btn = ctk.CTkButton(
            footer,
            text="✔ Save Configuration",
            height=40,
            width=180,
            font=("Consolas", 11, "bold"),
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary'],
            text_color=self.colors['bg_dark'],
            corner_radius=8,
            command=self.save_config
        )
        save_btn.pack(side="right")
    
    def clear_current(self):
        """Limpa o pick atual"""
        if 'entry' in self.content_widgets:
            self.content_widgets['entry'].delete(0, 'end')
            self.pick_values[self.current_tab] = ""
            self.update_tab_indicator(self.tab_buttons[self.current_tab], self.current_tab)
    
    def save_config(self):
        """Salva configuração"""
        # Salvar valor da aba atual
        if 'entry' in self.content_widgets:
            self.pick_values[self.current_tab] = self.content_widgets['entry'].get().strip()
        
        pick1 = self.pick_values[0].strip()
        pick2 = self.pick_values[1].strip()
        pick3 = self.pick_values[2].strip()
        
        # Validar 1º pick
        if not pick1:
            messagebox.showerror(
                "Error",
                "1st Pick is required!\n\nPlease configure your main champion.",
                parent=self.dialog
            )
            self.show_tab(0)
            return
        
        # Configurar no app
        if not self.app.instalock_autoban.set_instalock_champion(pick1):
            messagebox.showerror("Error", f"Invalid champion: {pick1}", parent=self.dialog)
            return
        
        self.app.instalock_champion = pick1
        
        # Configurar backups
        if pick2:
            if not self.app.instalock_autoban.set_instalock_backup_2(pick2):
                messagebox.showerror("Error", f"Invalid 2nd backup: {pick2}", parent=self.dialog)
                return
            self.app.instalock_backup_2 = pick2
        else:
            self.app.instalock_autoban.instalock_backup_2 = "None"
            self.app.instalock_backup_2 = None
        
        if pick3:
            if not self.app.instalock_autoban.set_instalock_backup_3(pick3):
                messagebox.showerror("Error", f"Invalid 3rd backup: {pick3}", parent=self.dialog)
                return
            self.app.instalock_backup_3 = pick3
        else:
            self.app.instalock_autoban.instalock_backup_3 = "None"
            self.app.instalock_backup_3 = None
        
        # Atualizar UI
        self.app.update_instalock_card()
        
        # Logs
        print(f"\n✅ Instalock configured:")
        print(f"  1st: {self.app.instalock_champion}")
        print(f"  2nd: {self.app.instalock_backup_2 or 'None'}")
        print(f"  3rd: {self.app.instalock_backup_3 or 'None'}")
        
        messagebox.showinfo(
            "Success",
            f"Instalock configured successfully!\n\n"
            f"1st Pick: {pick1}\n"
            f"2nd Pick: {pick2 or 'None'}\n"
            f"3rd Pick: {pick3 or 'None'}",
            parent=self.dialog
        )
        
        self.close()
    
    def cancel(self):
        """Cancela e fecha"""
        self.close()
    
    def close(self):
        """Fecha janela"""
        try:
            self.dialog.grab_release()
            self.dialog.destroy()
        except:
            pass


# Função para ser chamada no main.py
def open_modern_instalock_config(parent, app):
    """Abre configurador moderno de instalock"""
    ModernInstalockConfigurator(parent, app)