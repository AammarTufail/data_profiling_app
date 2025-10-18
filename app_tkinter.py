import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import seaborn as sns
from ydata_profiling import ProfileReport
import webbrowser
import os
import tempfile
from tkinterweb import HtmlFrame

class DataProfilingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Data Profiling App by Codanics.com")
        self.root.geometry("1400x800")
        
        self.df = None
        self.current_report_path = None
        
        # Sample datasets
        self.sample_datasets = {
            "None": None,
            "Diamonds": "diamonds",
            "Tips": "tips",
            "Flights": "flights",
            "Iris": "iris",
            "Titanic": "titanic"
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=3)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel
        left_panel = ttk.LabelFrame(main_frame, text="Data Upload & Control", padding="10")
        left_panel.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Upload section
        ttk.Label(left_panel, text="Upload CSV File:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        upload_btn = ttk.Button(left_panel, text="📁 Browse & Upload CSV", command=self.upload_file)
        upload_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Sample datasets section
        ttk.Label(left_panel, text="Or Choose Sample Dataset:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        
        self.sample_var = tk.StringVar(value="None")
        sample_dropdown = ttk.Combobox(left_panel, textvariable=self.sample_var, 
                                       values=list(self.sample_datasets.keys()), state='readonly')
        sample_dropdown.pack(fill=tk.X, pady=(0, 10))
        sample_dropdown.bind('<<ComboboxSelected>>', self.load_sample_dataset)
        
        # Status section
        ttk.Separator(left_panel, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(left_panel, text="Status:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        self.status_text = tk.Text(left_panel, height=4, wrap=tk.WORD, state='disabled')
        self.status_text.pack(fill=tk.X, pady=(0, 10))
        
        # Action buttons
        ttk.Separator(left_panel, orient='horizontal').pack(fill=tk.X, pady=10)
        
        self.generate_btn = ttk.Button(left_panel, text="🔍 Generate Profiling Report", 
                                       command=self.generate_report, state='disabled')
        self.generate_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.download_btn = ttk.Button(left_panel, text="📥 Download Report as HTML", 
                                       command=self.download_report, state='disabled')
        self.download_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.open_browser_btn = ttk.Button(left_panel, text="🌐 Open in Browser", 
                                           command=self.open_in_browser, state='disabled')
        self.open_browser_btn.pack(fill=tk.X)
        
        # Top right - header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(header_frame, text="📊 Data Profiling App by Codanics.com", 
                 font=('Arial', 16, 'bold')).pack(anchor=tk.W)
        ttk.Label(header_frame, text="Upload your dataset or try with sample data to generate an automated profiling report",
                 font=('Arial', 9)).pack(anchor=tk.W)
        
        # Bottom right - tabbed view
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Data Preview Tab
        preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(preview_frame, text="Data Preview")
        
        # Treeview for data preview
        preview_scroll_y = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL)
        preview_scroll_x = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL)
        
        self.tree = ttk.Treeview(preview_frame, 
                                yscrollcommand=preview_scroll_y.set,
                                xscrollcommand=preview_scroll_x.set)
        
        preview_scroll_y.config(command=self.tree.yview)
        preview_scroll_x.config(command=self.tree.xview)
        
        preview_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        preview_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Report Tab
        report_frame = ttk.Frame(self.notebook)
        self.notebook.add(report_frame, text="Profiling Report")
        
        # Try to use tkinterweb HtmlFrame, fallback to Text widget
        try:
            self.html_frame = HtmlFrame(report_frame)
            self.html_frame.pack(fill=tk.BOTH, expand=True)
            self.use_html_frame = True
        except:
            # Fallback to text widget with message
            self.report_text = tk.Text(report_frame, wrap=tk.WORD)
            report_scroll = ttk.Scrollbar(report_frame, orient=tk.VERTICAL, command=self.report_text.yview)
            self.report_text.config(yscrollcommand=report_scroll.set)
            report_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            self.report_text.pack(fill=tk.BOTH, expand=True)
            self.use_html_frame = False
        
        self.update_status("👆 Please upload a CSV file or select a sample dataset to get started")
    
    def update_status(self, message):
        self.status_text.config(state='normal')
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, message)
        self.status_text.config(state='disabled')
    
    def upload_file(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                self.sample_var.set("None")
                self.update_status(f"✅ File uploaded successfully!\nShape: {self.df.shape}\nRows: {self.df.shape[0]}, Columns: {self.df.shape[1]}")
                self.display_preview()
                self.generate_btn.config(state='normal')
            except Exception as e:
                messagebox.showerror("Error", f"Error reading file: {str(e)}")
                self.update_status(f"❌ Error reading file: {str(e)}")
    
    def load_sample_dataset(self, event=None):
        selected = self.sample_var.get()
        
        if selected == "None":
            return
        
        try:
            dataset_name = self.sample_datasets[selected]
            self.df = sns.load_dataset(dataset_name)
            self.update_status(f"📋 Loaded sample dataset: {selected}\nShape: {self.df.shape}\nRows: {self.df.shape[0]}, Columns: {self.df.shape[1]}")
            self.display_preview()
            self.generate_btn.config(state='normal')
        except Exception as e:
            messagebox.showerror("Error", f"Error loading sample dataset: {str(e)}")
            self.update_status(f"❌ Error loading sample dataset: {str(e)}")
    
    def display_preview(self):
        # Clear existing data
        self.tree.delete(*self.tree.get_children())
        
        # Configure columns
        self.tree['columns'] = list(self.df.columns)
        self.tree['show'] = 'headings'
        
        # Set column headings
        for col in self.df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=50)
        
        # Insert data (first 100 rows)
        for idx, row in self.df.head(100).iterrows():
            self.tree.insert('', tk.END, values=list(row))
    
    def generate_report(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        self.update_status("⏳ Generating profiling report... Please wait...")
        self.root.update()
        
        try:
            dataset_name = self.sample_var.get() if self.sample_var.get() != "None" else "Uploaded Dataset"
            
            profile = ProfileReport(
                self.df,
                title=f"Profiling Report - {dataset_name}",
                explorative=True
            )
            
            # Save to temporary file
            temp_dir = tempfile.gettempdir()
            self.current_report_path = os.path.join(temp_dir, f"profiling_report_{dataset_name.lower().replace(' ', '_')}.html")
            profile.to_file(self.current_report_path)
            
            # Display report
            if self.use_html_frame:
                self.html_frame.load_file(self.current_report_path)
            else:
                self.report_text.delete(1.0, tk.END)
                self.report_text.insert(1.0, f"Report generated successfully!\n\n"
                                            f"To view the full interactive report:\n"
                                            f"1. Click 'Open in Browser' button\n"
                                            f"2. Or click 'Download Report as HTML' and open the file\n\n"
                                            f"Report location: {self.current_report_path}")
            
            self.notebook.select(1)  # Switch to report tab
            self.download_btn.config(state='normal')
            self.open_browser_btn.config(state='normal')
            
            self.update_status(f"✅ Report generated successfully!\nDataset: {dataset_name}")
            messagebox.showinfo("Success", "Profiling report generated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {str(e)}")
            self.update_status(f"❌ Error generating report: {str(e)}")
    
    def download_report(self):
        if not self.current_report_path or not os.path.exists(self.current_report_path):
            messagebox.showwarning("Warning", "No report generated yet!")
            return
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")],
            initialfile="profiling_report.html"
        )
        
        if save_path:
            try:
                with open(self.current_report_path, 'r', encoding='utf-8') as src:
                    with open(save_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                messagebox.showinfo("Success", f"Report saved to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving report: {str(e)}")
    
    def open_in_browser(self):
        if not self.current_report_path or not os.path.exists(self.current_report_path):
            messagebox.showwarning("Warning", "No report generated yet!")
            return
        
        try:
            webbrowser.open('file://' + os.path.abspath(self.current_report_path))
        except Exception as e:
            messagebox.showerror("Error", f"Error opening browser: {str(e)}")

def main():
    root = tk.Tk()
    app = DataProfilingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
