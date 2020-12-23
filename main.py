from bokeh.layouts import column, layout, row, Spacer
from bokeh.plotting import curdoc
from bokeh.models import Button, TextInput, CheckboxButtonGroup
from bokeh.models.widgets import Div

######
# BASIC/ALWAYS-ON UI ELEMENTS
######

# define top part of the layout: buttons to add new items and to define partyumsatz without gastgeberumsatz
info_div = Div(text="Left column allows to interactively add and remove data. Right column computes coupon value and unused coupon value. Final sum is shown to the bottom left.", width=720)
add_item_button = Button(label="+ Produkt", button_type="success", width=380)

turnover_input_default_value = "Partyumsatz (ohne GG) hier eingeben"
turnover_input = TextInput(value=turnover_input_default_value)

coupon_value_passive_default_value = "?? € Gutscheinwert"
coupon_value_passive = TextInput(value=coupon_value_passive_default_value, disabled=True)

# bottom part of layout: info how much to pay/or how much coupon is "goes to waste"
zahlbetrag_passive_default_value = "?? € Endsumme"
zahlbetrag_passive = TextInput(value=zahlbetrag_passive_default_value, disabled=True, width=380)

coupon_remainder_passive_default_value = "?? € Restgutschein"
coupon_remainder_passive = TextInput(value=coupon_remainder_passive_default_value, disabled=True)



######
# LAYOUTING
######
item_data_column_layout = column()
coupon_value_column_layout = column(coupon_value_passive)
outer_column_layout = column(   info_div,
                                row(add_item_button, turnover_input),
                                row(item_data_column_layout, coupon_value_column_layout),
                                row(zahlbetrag_passive, coupon_remainder_passive)
                                )

######
# LISTENERS AND HOOKS AND FUNCTIONS
######

def update_coupon_and_endsum(*args):
    party_turnover = turnover_input.value
    item_prices = []
    use_coupon_toggles = []
    for item in item_data_column_layout.children:
        item_prices.append(item.children[0].value)
        use_coupon_toggles.append(item.children[2].active)

    try:
        party_turnover = float(party_turnover.replace(',','.'))
        item_prices = [float(p.replace(',','.')) for p in item_prices]
        use_coupon_toggles = [len(c)>0 for c in use_coupon_toggles]

        coupon_value = 0.1*party_turnover
        item_cost = 0
        cost_redeemed_via_coupons = 0

        for i in range(len(item_prices)):
            coupon_value += 0.1 * item_prices[i] * (not use_coupon_toggles[i])
            item_cost += item_prices[i]
            cost_redeemed_via_coupons += item_prices[i] * use_coupon_toggles[i]

        zahlbetrag = max(item_cost - min(cost_redeemed_via_coupons, coupon_value), 0)
        coupon_remainder = max(coupon_value - cost_redeemed_via_coupons, 0)

        # set output field stati
        coupon_value_passive.value = "{:.2f} € Gutscheinwert".format(coupon_value)
        coupon_remainder_passive.value = "{:.2f} € Restgutschein".format(coupon_remainder)
        zahlbetrag_passive.value = "{:.2f} € Endsumme".format(zahlbetrag)


    except:
        coupon_value_passive.value = coupon_value_passive_default_value
        coupon_remainder_passive.value = coupon_remainder_passive_default_value
        zahlbetrag_passive.value = zahlbetrag_passive_default_value

def update_coupon_and_endsum_wrapper(attr, old, new):
    update_coupon_and_endsum()

def add_item():
    item_price_input = TextInput(value="[Preis]", width=140)
    item_name_input = TextInput(value="[Produkt]", width=140)
    toggle_as_coupon_button = CheckboxButtonGroup(labels=['G'], active=[], width_policy="min")
    remove_item_button = Button(label='X', width_policy='min', button_type='warning')
    this_layout = row(item_price_input, item_name_input, toggle_as_coupon_button, remove_item_button)

    def remove_this_item(*args):
        item_data_column_layout.children.remove(this_layout)
        if len(item_data_column_layout.children) == 0:
            add_item() #avoid empty layout
        else:
            update_coupon_and_endsum()

    remove_item_button.on_click(remove_this_item)
    toggle_as_coupon_button.on_click(update_coupon_and_endsum)
    item_price_input.on_change('value', update_coupon_and_endsum_wrapper)
    item_data_column_layout.children.append(this_layout)
    update_coupon_and_endsum()


# register functions and hooks
add_item_button.on_click(add_item)
turnover_input.on_change('value', update_coupon_and_endsum_wrapper)



######
# START APP
######

add_item()
curdoc().add_root(outer_column_layout)
