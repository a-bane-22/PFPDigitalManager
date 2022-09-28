# Pre:  security is a tuple containing (symbol, name, std dev, mean, quadrant, ratio)
# Post: RV = quadrant, ratio
def sort_ranked_securities(security):
    return security[4], security[5]
