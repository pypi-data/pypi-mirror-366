# MIMICX AI Library 📚

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/genai-processors.svg)](https://pypi.org/project/mimicx/)

**Create Human-Like AI: Perception, Reasoning, and Interaction in One Library**

Mimicx AI is a lightweight Python library for giving machines human-level perception and decision-making capabilities by enabling advanced perception, contextual reasoning, autonomous decision-making, and intuitive human-machine interaction.

At its core, Mimicx structures its capabilities into specialized domains — `Vision`, `Text`, `Voice`, `Feel`, `Twin`, `Phy`, `Sense`, and `Mind` — each targeting a unique dimension of machine perception, reasoning, and interaction.

## Sample: Face Recognition 

```python
from mimicx import Model

# Initialize load model
model = Model("mimicvision/face_recognition")

# Compare faces
result = model.compare_faces(image1_path, image2_path)
print(f"Face similarity: {result:.2f}")
       
```



## Sample: Iris Recognition 

```python
from mimicx import Model

# Initialize load model
model = Model("mimicvision/iris_recognition")

# Compare faces
result = model.compare_iris(image1_path, image2_path)
print(f"Iris similarity: {result}")

```


## Notes
* Ensure that the images exist in the same directory as this script.

* The MimicX package must be installed and properly configured.

* The load('face_recognition') call initializes the face recognition model.



## ✨ Key Features

*   **MimicVision**:  processes and interprets visual data, enabling advanced image and video understanding.

*   **MimicText**: handles natural language processing and contextual text reasoning.

*   **MimicVoice**: works with audio signals for speech recognition, synthesis, and voice interaction.

*   **MimicFeel**: captures and interprets tactile and sensory data to simulate touch and emotion.

*   **MimicTwin**: creates and manages digital twins, bridging physical and virtual environments.

*   **MimicPhy**: interfaces with physical systems for autonomous control and robotics.

*   **MimicSense**: integrates multisensory data streams for comprehensive environmental awareness.

*   **MimicMind**: enables high-level cognitive functions including planning, decision-making, and adaptive learning.


## 📦 Installation

The GenAI Processors library requires Python 3.10+.

Install it with:

```bash
pip install mimicx
```


## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for
guidelines on how to contribute to this project.

## 📜 License

This project is licensed under the MIT License, See the
[LICENSE](LICENSE) file for details.

## Mimicx Terms of Services

If you make use of Mimicx via the MimicX library, please ensure you
review the [Terms of Service](https://mimicx.ai).
