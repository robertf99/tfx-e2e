import tensorflow_transform as tft


def processing_fn(inputs):
    outputs = {}
    for key in [
        "bill_length_mm",
        "bill_depth_mm",
        "flipper_length_mm",
        "body_mass_g",
    ]:
        outputs[_transformed_name(key)] = tft.scale_to_z_score(inputs[key])
    for key in ["island", "sex"]:
        outputs[_transformed_name(key)] = tft.compute_and_apply_vocabulary(inputs[key])
    return outputs
