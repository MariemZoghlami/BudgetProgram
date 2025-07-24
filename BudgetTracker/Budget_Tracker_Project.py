

import flet as ft  # 1st: Import Flet for UI components
import datetime   # 2nd: Import datetime for date handling
import json       # 3rd: Import json for saving/loading data
import os         # 4th: Import os to check file existence
from collections import defaultdict  # 5th: For summing categories


DATA_FILE = "expenses.json"

months = ["All", "January", "February", "March", "April", "May", "June",
"July", "August", "September", "October", "November", "December"]

expenses = []

# 9th: Save expenses list to JSON file
def save_expenses():
    with open(DATA_FILE, "w") as f:
        json.dump([
            {
                "title": e["title"],
                "amount": e["amount"],
                "category": e["category"],
                "date": e["date"].strftime('%Y-%m-%d')  # Save date as string
            }
            for e in expenses
        ], f)

# 10th: Load expenses from JSON file (if exists)
def load_expenses():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            for item in data:
                expenses.append({
                    "title": item["title"],
                    "amount": item["amount"],
                    "category": item["category"],
                    "date": datetime.datetime.strptime(item["date"], '%Y-%m-%d').date()
                })

# 11th: Main function - the app starts here
def main(page: ft.Page):
    page.title = "💸 Enhanced Expense Tracker"  # Set window title
    page.theme_mode = ft.ThemeMode.DARK        # Dark theme for style
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO


    load_expenses()


    title_text = ft.Text("💰 Expense Tracker", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN)


    month_filter = ft.Dropdown(
        label="Filter by Month",
        options=[ft.dropdown.Option(m) for m in months],
        value="All"
    )

    
    title_input = ft.TextField(label="Title", width=200)
    amount_input = ft.TextField(label="Amount (₹)", width=120, keyboard_type=ft.KeyboardType.NUMBER)
    category_input = ft.Dropdown(
        label="Category",
        options=[
            ft.dropdown.Option("Food"),
            ft.dropdown.Option("Transport"),
            ft.dropdown.Option("Rent"),
            ft.dropdown.Option("Entertainment"),
            ft.dropdown.Option("Other"),
        ],
        value="Food",
        width=150
    )
    date_picker = ft.DatePicker(
    first_date=datetime.date(2023, 1, 1),
    last_date=datetime.date.today(),
    value=datetime.date.today()
)
    page.overlay.append(date_picker)  # Needed for DatePicker popup

    # 16th: Pie chart to show category distribution
    pie_chart = ft.PieChart(
        sections=[],
        sections_space=2,
        center_space_radius=40,
        expand=True
    )

    # 17th: Text to show total expenses
    total_text = ft.Text("", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER)

    # 18th: Column to show list of expenses with delete buttons
    expense_list = ft.Column()

    # 19th: Function to update the pie chart based on filtered data
    def update_pie_chart():
        selected_month = month_filter.value
        category_totals = defaultdict(float)

        for e in expenses:
            exp_month = e["date"].strftime('%B')
            if selected_month == "All" or exp_month == selected_month:
                category_totals[e["category"]] += e["amount"]

        pie_chart.sections = [
            ft.PieChartSection(
                value=amt,
                title=f"{cat}\n₹{amt:.2f}",
                color=ft.Colors.CYAN if i % 2 == 0 else ft.Colors.TEAL
            )
            for i, (cat, amt) in enumerate(category_totals.items())
        ]
        pie_chart.update()

    # 20th: Function to refresh the UI lists and total based on current filter
    def refresh_ui():
        selected_month = month_filter.value
        filtered = []
        total = 0
        for idx, exp in enumerate(expenses):
            exp_month = exp["date"].strftime('%B')
            if selected_month == "All" or exp_month == selected_month:
                filtered.append((idx, exp))
                total += exp["amount"]

        # Clear and rebuild expense list UI
        expense_list.controls.clear()
        for idx, exp in filtered:
            expense_card = ft.Card(
                content=ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column([
                                ft.Text(exp["title"], weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Text(f"₹{exp['amount']:.2f} | {exp['category']} | {exp['date'].strftime('%d %b %Y')}",
                                        color=ft.Colors.GREY_400)
                            ]),
                            ft.IconButton(
                                ft.icons.DELETE,
                                on_click=lambda e, i=idx: delete_expense(i),
                                icon_color=ft.Colors.RED_ACCENT
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=15,
                ),
                elevation=3,
                color=ft.colors.with_opacity(0.1, ft.Colors.WHITE),
                shape=ft.RoundedRectangleBorder(radius=10)
            )
            expense_list.controls.append(expense_card)

        total_text.value = f"Total for {selected_month}: ₹{total:.2f}"
        page.update()

    # 21st: Function to add a new expense from input fields
    def add_expense(e):
        if not (title_input.value and amount_input.value and category_input.value and date_picker.value):
            return  # Do nothing if any input missing

        try:
            amount = float(amount_input.value)
        except ValueError:
            return  # Invalid amount input

        expenses.append({
            "title": title_input.value,
            "amount": amount,
            "category": category_input.value,
            "date": date_picker.value
        })

        save_expenses()  # Save to file

        # Clear inputs after adding
        title_input.value = ""
        amount_input.value = ""
        category_input.value = "Food"
        date_picker.value = datetime.date.today()

        refresh_ui()
        update_pie_chart()

    # 22nd: Function to delete an expense by index
    def delete_expense(idx):
        expenses.pop(idx)
        save_expenses()
        refresh_ui()
        update_pie_chart()

        def fill_today_date(e):
            date_picker.value = datetime.date.today()
        date_picker.update()

    add_date_button = ft.ElevatedButton("📅 Add Today’s Date", on_click=fill_today_date, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)))


    add_button = ft.ElevatedButton("➕ Add Expense", on_click=add_expense, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)))

 
    input_row = ft.ResponsiveRow([
    title_input,
    amount_input,
    category_input,
    date_picker,
    add_button
], spacing=10, run_spacing=10)

    # 25th: When month filter changes, refresh UI and chart
    def on_month_change(e):
        refresh_ui()
        update_pie_chart()

    month_filter.on_change = on_month_change

    # 26th: Add all components to the page
    page.add(
        ft.Column([
            title_text,
            month_filter,
            input_row,
            total_text,
            ft.Container(content=pie_chart, width=400, height=400),
            ft.Divider(),
            expense_list
        ])
    )

    # 27th: Initial UI update on app start
    refresh_ui()
    update_pie_chart()

# 28th: Start the app with main function

#input("Press Enter to exit...")

ft.app(target=main)

