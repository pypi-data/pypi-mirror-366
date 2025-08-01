"""
Implement model-specific inference functions for foundation models.
"""

import torch

from torch import nn


def __extract_features_uni(
    images: torch.Tensor,
    model: nn.Module,
    transform: nn.Module,
) -> torch.Tensor:
    """
    --> See https://huggingface.co/MahmoodLab/UNI

    Extracts features from images using the UNI model.
    Assumes image and model in the same device.

    DON'T use this function directly

    :param images: Batch tensor of shape (N, 3, H, W)
    :param model: The UNI model
    :param transform: the preprocessing transform
    :return: Extracted features
    """
    image_tensor = transform(images)
    with torch.inference_mode():
        features = model(image_tensor)
    return features


def __extract_features_uni2h(
    images: torch.Tensor,
    model: nn.Module,
    transform: nn.Module,
) -> torch.Tensor:
    """
    --> See https://huggingface.co/MahmoodLab/UNI2-h

    Extracts features from images using the UNI2-h model.
    Assumes image and model in the same device.

    DON'T use this function directly

    :param images: Batch tensor of shape (N, 3, H, W)
    :param model: The UNI2-h model
    :param transform: the preprocessing transform
    :return: Extracted features
    """
    image_tensor = transform(images)
    with torch.inference_mode():
        features = model(image_tensor)
    return features


def __extract_features_phikon(
    images: torch.Tensor,
    model: nn.Module,
    transform: nn.Module,
) -> torch.Tensor:
    """
    --> See https://github.com/owkin/HistoSSLscaling/

    Extracts features from images using the Phikon model.
    Assumes image and model in the same device.

    DON'T use this function directly

    :param images: Batch tensor of shape (N, 3, H, W)
    :param model: The Phikon model
    :param transform: the preprocessing transform
    :return: Extracted features
    """
    # process the image
    inputs = transform(images, return_tensors="pt")
    # cast back to original device
    inputs = {k: v.to(images.device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        features = outputs.last_hidden_state[:, 0, :]
    return features


def __extract_features_phikon_v2(
    images: torch.Tensor,
    model: nn.Module,
    transform: nn.Module,
) -> torch.Tensor:
    """
    --> See https://huggingface.co/owkin/phikon-v2

    Extracts features from images using the Phikon v2 model.

    DON'T use this function directly

    :param images: Batch tensor of shape (N, 3, H, W)
    :param model: The Phikon v2 model
    :param transform: the preprocessing transform
    :return: Extracted features
    """
    inputs = transform(images, return_tensors="pt")
    # cast back to original device
    inputs = {k: v.to(images.device) for k, v in inputs.items()}

    with torch.inference_mode():
        outputs = model(**inputs)
        features = outputs.last_hidden_state[:, 0, :]
    return features


def __extract_features_h_optimus_0(
    images: torch.Tensor,
    model: nn.Module,
    transform: nn.Module,
) -> torch.Tensor:
    """
    --> See https://huggingface.co/bioptimus/H-optimus-0 (adapted to work with tensors)

    Extracts features from images using the H-Optimus-0 model.
    Assumes image and model in the same device.

    DON'T use this function directly

    :param images: Batch tensor of shape (N, 3, H, W)
    :param model: The H-Optimus-0 model
    :param transform: the preprocessing transform
    :return: Extracted features
    """
    with torch.autocast(device_type="cuda", dtype=torch.float16):
        with torch.inference_mode():
            # (C, H, W) -> (H, W, C)
            numpy_images = [image.permute(1, 2, 0).cpu().numpy() for image in images]
            preprocessed_images = torch.stack(
                [transform(image) for image in numpy_images]
            )  # (N, C, H, W)
            features = model(preprocessed_images.to(images.device))
    return features


def __extract_features_hibou_b(
    images: torch.Tensor,
    model: nn.Module,
    transform: nn.Module,
) -> torch.Tensor:
    """
    --> See https://huggingface.co/histai/hibou-b

    Extracts features from images using the Hibou-B model.
    Assumes image and model in the same device.

    DON'T use this function directly

    NOTE: Hibou-B uses DinoV2 arch so
    features are the first token of the last hidden state. Same as Phikon.

    :param images: Batch tensor of shape (N, 3, H, W)
    :param model: The Hibou-B model
    :param transform: the preprocessing transform
    :return: Extracted features
    """
    inputs = transform(images, return_tensors="pt")
    # cast back to original device
    inputs = {k: v.to(images.device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        features = outputs.last_hidden_state[:, 0, :]
    return features


def __extract_features_hibou_L(
    images: torch.Tensor,
    model: nn.Module,
    transform: nn.Module,
) -> torch.Tensor:
    """
    --> See https://huggingface.co/histai/hibou-L

    Extracts features from images using the Hibou-L model.
    Assumes image and model in the same device.

    DON'T use this function directly

    NOTE: Hibou-L uses DinoV2 arch so
    features are the first token of the last hidden state. Same as Phikon.

    :param images: Batch tensor of shape (N, 3, H, W)
    :param model: The Hibou-L model
    :param transform: the preprocessing transform
    :return: Extracted features
    """
    inputs = transform(images, return_tensors="pt")
    # cast back to original device
    inputs = {k: v.to(images.device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        features = outputs.last_hidden_state[:, 0, :]
    return features


def __extract_features_virchow(
    images: torch.Tensor,
    model: nn.Module,
    transform: nn.Module,
) -> torch.Tensor:
    """
    --> See https://huggingface.co/paige-ai/Virchow

    Extracts features from images using the Virchow model.
    Assumes image and model in the same device.

    DON'T use this function directly

    :param images: Batch tensor of shape (N, 3, H, W)
    :param model: The Virchow model
    :param transform: the preprocessing transform
    :return: Extracted features
    """
    images = transform(images)
    # model deck recommends running inference in mixed precision (autocast mode, f16)
    # so we do that
    with torch.inference_mode(), torch.autocast(
        device_type="cuda", dtype=torch.float16
    ):
        output = model(images)
    class_tokens = output[:, 0]  # (N, 1280)
    patch_tokens = output[:, 1:]  # (N, 256, 1280)
    # concatenate class token and average pool of patch tokens
    features = torch.cat([class_tokens, patch_tokens.mean(dim=1)], dim=-1)  # (N, 2560)
    return features


def __extract_features_virchow_v2(
    images: torch.Tensor,
    model: nn.Module,
    transform: nn.Module,
) -> torch.Tensor:
    """
    --> See https://huggingface.co/paige-ai/Virchow2

    Extracts features from images using the Virchow2 model.
    Assumes image and model in the same device.

    DON'T use this function directly

    :param images: Batch tensor of shape (N, 3, H, W)
    :param model: The Virchow2 model
    :param transform: the preprocessing transform
    :return: Extracted features
    """
    images = transform(images)
    # model deck recommends running inference in mixed precision (autocast mode, f16)
    # so we do that
    with torch.inference_mode(), torch.autocast(
        device_type="cuda", dtype=torch.float16
    ):
        output = model(images)  # (N, 261, 2560)
    class_tokens = output[:, 0]  # (N, 2560)
    # NOTE: tokens 1-4 are REGISTER tokens according to the model card
    # so we must ignore them
    patch_tokens = output[:, 5:]  # (N, 256, 2560)
    # concatenate class token and average pool of patch tokens
    features = torch.cat([class_tokens, patch_tokens.mean(dim=1)], dim=-1)  # (N, 2560)
    return features
