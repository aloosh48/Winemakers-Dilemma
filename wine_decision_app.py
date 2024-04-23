# Logic for calculating E-values
import gradio as gr

# Initialize the probabilities with Alejandro's initial beliefs
prob_storm = 0.5  # Probability of a storm
prob_norot_sweet = 0.6  # Probability of no sugar increase without storm
prob_typical_sweet = 0.3  # Probability of typical sugar increase without storm
prob_high_sweet = 0.1  # Probability of high sugar increase without storm

# E-Value without model to be used for comparison
e_value_without_model = 928500

# Logic for calculating E-values
def calculate_e_values(prob_storm, prob_botrytis, prob_norot_sweet, prob_typical_sweet, prob_high_sweet, sensitivity=0.83, specificity=0.87):
    # Market revenues per bottle for each Riesling type
    revenue_per_bottle = {
        "Trocken": 5,
        "Kabinett": 10,
        "Spätlese": 15,
        "Auslese": 30,
        "Beerenauslese": 40,
        "Trockenbeerenauslese": 120
    }
    
    # Number of cases produced under different scenarios
    cases = {
        "Harvest Now": {"Trocken": 6000, "Kabinett": 2000, "Spätlese": 2000},
        "Storm-No Mold": {"Trocken": 5000, "Kabinett": 1000},
        "Storm-Mold": {"Trockenbeerenauslese": 2000},
        "No Storm-No Sugar": {"Trocken": 6000, "Kabinett": 2000, "Spätlese": 2000},
        "No Storm-Typical Sugar": {"Trocken": 5000, "Kabinett": 1000, "Spätlese": 2500, "Auslese": 1500},
        "No Storm-High Sugar": {"Trocken": 4000, "Kabinett": 2500, "Spätlese": 2000, "Auslese": 1000, "Beerenauslese": 500}
    }

    prob_storm_corrected = prob_storm * sensitivity + (1 - prob_storm) * (1 - specificity)
    prob_no_storm_corrected = (1 - prob_storm) * specificity + prob_storm * (1 - sensitivity)

    # Revenue calculations for different scenarios
    storm_revenue = (prob_botrytis * cases["Storm-Mold"]["Trockenbeerenauslese"] * 12 * revenue_per_bottle["Trockenbeerenauslese"]) + \
                    ((1 - prob_botrytis) * (cases["Storm-No Mold"]["Trocken"] * 12 * revenue_per_bottle["Trocken"] +
                                            cases["Storm-No Mold"]["Kabinett"] * 12 * revenue_per_bottle["Kabinett"]))

    no_sugar_revenue = cases["No Storm-No Sugar"]["Trocken"] * 12 * revenue_per_bottle["Trocken"] + \
                       cases["No Storm-No Sugar"]["Kabinett"] * 12 * revenue_per_bottle["Kabinett"] + \
                       cases["No Storm-No Sugar"]["Spätlese"] * 12 * revenue_per_bottle["Spätlese"]

    typical_sugar_revenue = cases["No Storm-Typical Sugar"]["Trocken"] * 12 * revenue_per_bottle["Trocken"] + \
                            cases["No Storm-Typical Sugar"]["Kabinett"] * 12 * revenue_per_bottle["Kabinett"] + \
                            cases["No Storm-Typical Sugar"]["Spätlese"] * 12 * revenue_per_bottle["Spätlese"] + \
                            cases["No Storm-Typical Sugar"]["Auslese"] * 12 * revenue_per_bottle["Auslese"]

    high_sugar_revenue = cases["No Storm-High Sugar"]["Trocken"] * 12 * revenue_per_bottle["Trocken"] + \
                         cases["No Storm-High Sugar"]["Kabinett"] * 12 * revenue_per_bottle["Kabinett"] + \
                         cases["No Storm-High Sugar"]["Spätlese"] * 12 * revenue_per_bottle["Spätlese"] + \
                         cases["No Storm-High Sugar"]["Auslese"] * 12 * revenue_per_bottle["Auslese"] + \
                         cases["No Storm-High Sugar"]["Beerenauslese"] * 12 * revenue_per_bottle["Beerenauslese"]

    # Calculate the total revenue and determine the recommended action
    total_revenue = (storm_revenue * prob_storm_corrected) + \
                    ((no_sugar_revenue * prob_norot_sweet) +
                     (typical_sugar_revenue * prob_typical_sweet) +
                     (high_sugar_revenue * prob_high_sweet)) * prob_no_storm_corrected

    e_value = total_revenue
    recommended_action = "Wait" if total_revenue > 928500 else "Harvest Now"

    return f"Expected Value (E-value) of the Decision: ${e_value}", f"Recommended Course of Action: {recommended_action}"

# Gradio interface setup
iface = gr.Interface(
    fn=calculate_e_values,
    inputs=[
        gr.Slider(0, 1, step=0.01, label="Probability of Storm", value=prob_storm),
        gr.Slider(0, 1, step=0.01, label="Probability of Botrytis if Storm", value=0.1),
        gr.Slider(0, 1, step=0.01, label="Probability of No Sugar Increase", value=prob_norot_sweet),
        gr.Slider(0, 1, step=0.01, label="Probability of Typical Sugar Increase", value=prob_typical_sweet),
        gr.Slider(0, 1, step=0.01, label="Probability of High Sugar Increase", value=prob_high_sweet)
    ],
    outputs=["text", "text"],
    title="Wine Production Decision Model"
)

# Run the Gradio app
iface.launch(share=False)
