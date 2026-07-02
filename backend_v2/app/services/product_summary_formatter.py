from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from app.schemas.enterprise_product_dto import EnterpriseProductDTO

class ProductSummaryFormatter:
    """
    Generates a professional Product Summary Card from an EnterpriseProductDTO.
    Returns a Rich renderable object.
    """

    def generate_summary(self, dto: EnterpriseProductDTO) -> Panel:
        
        # 1. Product Info Table
        product_table = Table(show_header=False, box=None, padding=(0, 2))
        product_table.add_column("Key", style="cyan", justify="right")
        product_table.add_column("Value", style="white")

        product_name = dto.product.name.value if dto.product.name else "Unknown"
        brand = dto.product.brand.value if dto.product.brand else "Unknown"
        barcode_str = dto.barcode.barcode if dto.barcode else "None"
        country = dto.barcode.country_of_origin if dto.barcode and dto.barcode.country_of_origin else "Unknown"

        product_table.add_row("Product Name:", f"[bold]{product_name}[/bold]")
        product_table.add_row("Brand:", brand)
        product_table.add_row("Barcode:", f"{barcode_str} ({country})")

        # 2. Dates & Batch Table
        dates_table = Table(show_header=False, box=None, padding=(0, 2))
        dates_table.add_column("Key", style="cyan", justify="right")
        dates_table.add_column("Value", style="green")

        mfg = dto.manufacturing.date.value if dto.manufacturing.date else "N/A"
        exp = dto.expiry.date.value if dto.expiry.date else "N/A"
        batch = dto.batch.batch_number.value if dto.batch.batch_number else "N/A"
        mrp = dto.pricing.mrp.value if dto.pricing.mrp else "N/A"

        dates_table.add_row("Manufacturing:", mfg)
        dates_table.add_row("Expiry Date:", f"[bold red]{exp}[/bold red]")
        dates_table.add_row("Batch Number:", batch)
        dates_table.add_row("MRP:", mrp)

        # 3. Validation Status
        val_text = Text()
        if dto.validation.is_valid:
            val_text.append("✅ ALL VALIDATIONS PASSED\n", style="bold green")
        else:
            val_text.append("❌ VALIDATION FAILED\n", style="bold red")

        if dto.alerts.errors:
            val_text.append("\nErrors:\n", style="bold red")
            for err in dto.alerts.errors:
                val_text.append(f" - {err}\n", style="red")

        if dto.alerts.warnings:
            val_text.append("\nWarnings:\n", style="bold yellow")
            for warn in dto.alerts.warnings:
                val_text.append(f" - {warn}\n", style="yellow")

        # Assemble Panel
        content = Group(
            product_table,
            Text("\n"),
            dates_table,
            Text("\n--- Validation & Status ---\n", style="dim"),
            val_text
        )

        status_color = "green" if dto.scan.status == "success" else ("yellow" if dto.scan.status == "warning" else "red")
        
        return Panel(
            content,
            title="[bold]Enterprise Product Summary[/bold]",
            border_style=status_color,
            padding=(1, 2)
        )
