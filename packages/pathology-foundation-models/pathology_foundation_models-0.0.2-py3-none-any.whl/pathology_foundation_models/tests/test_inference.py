import PIL
import torch
import pytest

from pathology_foundation_models.models.inference import (
    extract_features,
    extract_features_from_dataset,
    convert_to_batch_tensor,
)

# NOTE can't import enums twice with different import statements,
# see https://stackoverflow.com/questions/40371360/imported-enum-class-is-not-comparing-equal-to-itself
# so we import from models package
from pathology_foundation_models.models import (
    FoundationModelEnum,
    load_foundation_model,
)
from pathology_foundation_models.tests.fixtures import hf_token, image_dataset


@pytest.mark.parametrize(
    "model_type, expected_shape",
    [
        (FoundationModelEnum.UNI, (1, 1024)),
        (FoundationModelEnum.UNI2H, (1, 1536)),
        (FoundationModelEnum.PHIKON, (1, 768)),
        (FoundationModelEnum.PHIKON_V2, (1, 1024)),
        (FoundationModelEnum.H_OPTIMUS_0, (1, 1536)),
        (FoundationModelEnum.HIBOU_B, (1, 768)),
        (FoundationModelEnum.HIBOU_L, (1, 1024)),
        (FoundationModelEnum.VIRCHOW, (1, 2560)),
        (FoundationModelEnum.VIRCHOW_V2, (1, 2560)),
    ],
)
def test_inference_models_from_PIL(model_type, expected_shape, hf_token):
    image = PIL.Image.new("RGB", (224, 224), color="red")
    model = load_foundation_model(model_type, device="cuda", token=hf_token)
    features = extract_features(image, model)

    assert isinstance(features, torch.Tensor)
    assert features.shape == expected_shape


def test_batch_inference(hf_token, image_dataset):
    # inference was already tested, any model is fine for this test
    model = load_foundation_model(
        FoundationModelEnum.UNI, device="cuda", token=hf_token
    )
    batch_tensor = extract_features_from_dataset(
        image_dataset, model, batch_size=3, num_workers=2, display_progress=True
    )

    assert isinstance(batch_tensor, torch.Tensor)
    assert batch_tensor.shape == (len(image_dataset), 1024)


def test_convert_to_batch_tensor():
    image = PIL.Image.new("RGB", (224, 224), color="blue")
    batch_tensor = convert_to_batch_tensor(image)
    assert batch_tensor.shape == (1, 3, 224, 224)

    images = [image, PIL.Image.new("RGB", (224, 224), color="green")]
    batch_tensor = convert_to_batch_tensor(images)
    assert batch_tensor.shape == (2, 3, 224, 224)

    tensor_image = torch.rand(3, 224, 224)
    batch_tensor = convert_to_batch_tensor(tensor_image)
    assert batch_tensor.shape == (1, 3, 224, 224)
