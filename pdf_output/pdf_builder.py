from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Flowable, Spacer, Image, PageBreak, Paragraph
from reportlab.lib import colors

from game_data.iteration_utils.threat_pair import ThreatPair
from graphics.Game_Render import render_game, render_safe_steps


class TextBuilder:
    def __init__(self, story):
        self.story = story
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='Normal_CENTER',
                                       parent=self.styles['Normal'],
                                       fontName='Helvetica',
                                       wordWrap='LTR',
                                       alignment=TA_CENTER,
                                       fontSize=12,
                                       leading=13,
                                       textColor=colors.black,
                                       borderPadding=0,
                                       leftIndent=0,
                                       rightIndent=0,
                                       spaceAfter=0,
                                       spaceBefore=0,
                                       splitLongWords=True,
                                       spaceShrinkage=0.05,
                                       ))

    def center_text(self, text, style="Normal_CENTER"):
        self.story.append(Spacer(1, 6))
        self.story.append(Paragraph(text, self.styles[style]))
        self.story.append(Spacer(1, 6))

    def heading_text(self, text, style="h2"):
        self.story.append(Spacer(1, 12))
        self.story.append(Paragraph(text, self.styles[style]))
        # self.story.append(Spacer(1, 6))


def create_pdf(equilibria, game_graph):
    doc = SimpleDocTemplate("testing.pdf", pagesize=A4)
    story = []
    text_builder = TextBuilder(story)

    image_paths = create_image_paths(equilibria, game_graph)

    for eq_num, equilibrium in enumerate(equilibria, 1):
        text_builder.heading_text(f'Equilibrium {eq_num}', 'h1')

        for itr_num, iteration in enumerate(equilibrium, 1):
            itr_id = f'{eq_num}-{itr_num}'

            text_builder.heading_text(f'Iteration {itr_num}')
            story.append(add_game_images(itr_id, image_paths))

            if iteration.final_itr:
                text_builder.center_text('Final \u03B1 Vector')
                story.append(alpha_table(iteration.start_alpha))

                text_builder.center_text('Admissible Plans')
                story.append(admissible_plan_table(iteration.admissible_plans))
                break

            text_builder.center_text('Initial \u03B1 Vector')
            story.append(alpha_table(iteration.start_alpha))

            text_builder.center_text('Admissible Plans')
            story.append(admissible_plan_table(iteration.admissible_plans))

            text_builder.center_text(f'\u03B3 (U, \u03B1)')
            story.append(gamma_table(iteration.gamma_u))

            text_builder.center_text('Updated \u03B1 Vector')
            story.append(alpha_table(iteration.end_alpha))

    doc.build(story)


def admissible_plan_table(admissible_plans):
    table_heading = ['', 'F(U)', 'U(t)', 'Plan', 'Payoff', 'Condition']
    row_cnt = 1
    data = [table_heading]

    for plateau in admissible_plans:
        row = new_row(row_cnt)

        for state in list(plateau):
            row[1] += f'{state}, '

        row[1] = row[1][:-2]

        for u_map in admissible_plans[plateau]:
            row[2] = u_map_str(list(u_map))

            for plan in admissible_plans[plateau][u_map]:
                row[3] = plan
                row[4] = plan.state_payoff
                row[5] = plan.condition

                data.append(row)

                row_cnt += 1
                row = new_row(row_cnt)

    table = Table(data)
    table_style1 = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)])
    table.setStyle(table_style1)
    return table


def new_row(row_cnt):
    return [f'{row_cnt}.'] + ['' for _ in range(5)]


def u_map_str(u_map):
    out = ''
    for edge in u_map:
        out += f'U({edge[0]}) = {edge[1]}, '

    return out[:-2]


def u_map_dict(u_map):
    out = ''

    for state in u_map:
        out += f'U({state}) = {u_map[state]}, '

    return out[:-2]


def alpha_table(alpha):
    table_heading = ['State'] + [state for state in alpha]
    table_row = ['\u03B1'] + [alpha[state] for state in alpha]
    table = Table([table_heading, table_row])
    table_style1 = TableStyle([('BACKGROUND', (0, 0), (0, -1), colors.grey),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)])
    table.setStyle(table_style1)
    return table


def add_game_images(itr_id, image_paths):
    data = [[Image(image_paths[itr_id][0], width=200, height=200),
             Image(image_paths[itr_id][1], width=200, height=200)],
            ['Game', 'Safe Steps (Red)']]

    table = Table(data)
    style = TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')])
    table.setStyle(style)

    return table


def create_image_paths(equilibria, game_graph):
    image_paths = dict()
    game_dict = game_graph.neighbours_map

    for eq_num, equilibrium in enumerate(equilibria, 1):
        for itr_num, iteration in enumerate(equilibrium, 1):
            itr_id = f'{eq_num}-{itr_num}'
            alpha = iteration.start_alpha
            paths = [render_game(game_dict, alpha, f'{itr_id}-game'),
                     render_safe_steps(game_dict, alpha, iteration.safe_steps, f'{itr_id}-safe')]

            image_paths[itr_id] = paths

    return image_paths


def gamma_table(gamma_u):
    table_heading = ['', 'F(U)', 'U(t)', 'Plan', 'Payoff', 'Condition']
    row_cnt = 1
    data = [table_heading]
    row = new_row(row_cnt)
    for admiss in gamma_u:
        for state in admiss.u_map:
            row[1] += f'{state}, '

        row[1] = row[1][:-2]
        row[2] = u_map_dict(admiss.u_map)
        row[3] = admiss.plan
        row[4] = admiss.state_payoff

        condition = admiss.condition
        row[5] = condition

        if isinstance(condition, ThreatPair):
            pass

        data.append(row)
        row_cnt += 1
        row = new_row(row_cnt)

    table = Table(data)
    table_style1 = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)])
    table.setStyle(table_style1)
    return table
