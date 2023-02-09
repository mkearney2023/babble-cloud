import sys

project_dir = "/volumes/projects"
template_dir = "/templates"

from classes import Portfolio

portfolio = Portfolio(project_dir, template_dir)
print(portfolio.view(sys.argv[1]))