from flask import Flask, render_template, request, redirect, url_for
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os

app = Flask(__name__)

# Ensure the 'static' directory exists
if not os.path.exists('static'):
    os.makedirs('static')

# Define the page size and margins
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_LEFT = 4 * mm
MARGIN_RIGHT = 5 * mm
MARGIN_TOP = 17 * mm
MARGIN_BOTTOM = 12.7 * mm

# Define the label dimensions and spacing
LABEL_WIDTH = 48.5 * mm
LABEL_HEIGHT = 21.1 * mm
HORIZONTAL_PITCH = 1.8 * mm  # Horizontal space including gap between labels
VERTICAL_PITCH = 1.7 * mm    # Vertical space including gap between labels

LABEL_COLS = 4
LABEL_ROWS = 12

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            num_sets = int(request.form['num_sets'])
            all_labels_data = []

            for set_index in range(num_sets):
                num_labels = int(request.form[f'num_labels_{set_index}'])
                brand = request.form.get(f'brand_{set_index}')
                article = request.form.get(f'article_{set_index}')
                mrp = request.form.get(f'mrp_{set_index}')
                code = request.form.get(f'code_{set_index}')
                purchased_from = request.form.get(f'purchased_from_{set_index}')
                shop = request.form.get(f'shop_{set_index}')
                brand_font_size = int(request.form.get(f'brand_font_size_{set_index}', 14))
                mrp_font_size = int(request.form.get(f'mrp_font_size_{set_index}', 14))

                if not brand or not mrp:
                    return render_template('index.html', error="Please provide brand and MRP for all sets.")

                labels_data = []
                for label_index in range(num_labels):
                    labels_data.append({
                        'brand': brand.strip(),
                        'article': article.strip(),
                        'mrp': mrp.strip(),
                        'code': code.strip(),
                        'purchased_from': purchased_from.strip(),
                        'shop': shop.strip(),
                        'brand_font_size': brand_font_size,
                        'mrp_font_size': mrp_font_size
                    })

                all_labels_data.append(labels_data)

            create_pdf(all_labels_data)
            return redirect(url_for('download_labels'))
        except Exception as e:
            return render_template('index.html', error=f"An error occurred: {e}")

    return render_template('index.html')

def create_pdf(all_labels_data):
    doc = SimpleDocTemplate('static/labels.pdf', pagesize=A4, leftMargin=MARGIN_LEFT, rightMargin=MARGIN_RIGHT, topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM)
    elements = []
    styles = getSampleStyleSheet()
    text_style = ParagraphStyle(name='TextStyle', parent=styles['Normal'], fontSize=6, spaceAfter=3, wordWrap='CJK')

    for labels_data in all_labels_data:
        table_data = []
        row_heights = []

        for i in range(0, len(labels_data), LABEL_COLS):
            for j in range(LABEL_ROWS):
                if i + j * LABEL_COLS >= len(labels_data):
                    break

                row_data = []
                for k in range(LABEL_COLS):
                    index = i + j * LABEL_COLS + k
                    if index < len(labels_data):
                        label_info = labels_data[index]
                        content = f"<b>Brand:</b> {label_info['brand']}<br/>" \
                                  f"Article: {label_info['article']}<br/>" \
                                  f"<b>MRP:</b> {label_info['mrp']}<br/>" \
                                  f"Code: {label_info['code']}<br/>" \
                                  f"Purchased From: {label_info['purchased_from']}<br/>" \
                                  f"Shop: {label_info['shop']}"
                        row_data.append(Paragraph(content, text_style))
                    else:
                        row_data.append('')
                table_data.append(row_data)
                row_heights.append(LABEL_HEIGHT)

                # Add two divider rows between label rows
                if j < LABEL_ROWS - 1:
                    divider_row = ['' for _ in range(LABEL_COLS)]
                    table_data.append(divider_row)
                    table_data.append(divider_row)
                    row_heights.append(1)
                    row_heights.append(1)

            if i + (LABEL_ROWS * LABEL_COLS) >= len(labels_data):
                break

        table = Table(table_data, colWidths=[LABEL_WIDTH] * LABEL_COLS, rowHeights=row_heights)

        style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ])
        table.setStyle(style)

        elements.append(table)
        elements.append(Spacer(1, VERTICAL_PITCH))  # Add vertical pitch space

    doc.build(elements)

@app.route('/download')
def download_labels():
    return redirect(url_for('static', filename='labels.pdf'))

if __name__ == '__main__':
    app.run(debug=True)
