# Context-Aware Model Wrapper for Selective Quantization/Pruning and editing Attention Patterns

What I am currently doing (this may kinda read like a blog, I apologize in advance).

Benchmarking qualitative vs quantitative questions and seeing average gradient magnitudes.
This will hopefully allow me to quantize seemingly non important layers as I go on.

![fig1](https://github.com/AyanJhunjhunwala/ContextQ/blob/main/Figure_1.png "Initial Finding")

# Is the wrapper out? -> No

# Observations

Very initial but we see that atleast for the DiaboGPT-small model, the gradient mags are much more condensed for non reasoning and non open ended questions when compared to mathematical ones(simple questions)


# Use case

1. When thinking of strctured outputs from LLMs, and repetitve requests for generation, we can run context analysis and see gradients and their magnitudes. Using this, we can have layers quantized on requests.

2. We end up doing this anyway on the daily for models


# More thoughts

This is an extremely long project and I hope to be done with a prototype soon and continue working on it as long as I can. 


# Day by Day

This is just me keeping up with any progress I made.

# 13th July 2025

The attention patterns and gradient magnitude are obviously pretty different for quant/qual in dialo-small. I am planning to test this with a larger model. I tested out dialo with the ARC and GSM8k test. (below)

![fig2](https://github.com/AyanJhunjhunwala/ContextQ/blob/main/Figure_2.png)

I am going to switch over to llama 3.1 and benchmark 8-4 bit next. I am also going to work on attention patterns and quant strutcures for both quant/qual. This means a lot of reading for me :( 

# 17th July 2025

I am thinking of using github blogs for this but probably won't. So I ran the llama 3.1 8b instruct on ARC and svamp to split qualitative and quantitative and now my biggest question is how do I modify patterns and quantize the models to make this make sense. Svamp had a low accuracy and optmizing that without SFT would be something I guess. I started figruing out the pypi library as well but my main focus would have to be on extrapolating 

Benchmarks were ok...

# 21 July 2025

I have a roadmap! I will be implementing multi AWQ managed models and they will be able to be quantized more agressively. I will then implement a lightweight classifier that will figure out pre determined categories(much later obv)
