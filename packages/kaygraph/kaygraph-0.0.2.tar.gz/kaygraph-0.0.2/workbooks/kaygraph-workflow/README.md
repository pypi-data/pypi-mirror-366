# KayGraph Writing Workflow

A complete content creation workflow demonstrating multi-stage processing with KayGraph.

## What it does

This workflow automates content creation through four stages:
1. **Topic Validation**: Ensures valid input and prepares metadata
2. **Outline Generation**: Creates structured outline based on word count
3. **Content Writing**: Writes content following the outline
4. **Style Application**: Applies chosen writing style

## How to run

```bash
python main.py
```

## Features

- **ValidatedNode**: Input validation for topics
- **Multi-stage Pipeline**: Sequential processing steps
- **Style Variations**: Professional, casual, educational, motivational
- **Audience Targeting**: Content adapted for specific audiences
- **Error Handling**: Retries for writing stage

## Workflow Structure

```
TopicNode → OutlineNode → WritingNode → StyleNode
```

## Available Styles

- **Professional**: Formal tone, sophisticated vocabulary
- **Casual**: Conversational, simple language
- **Educational**: Instructive, clear explanations
- **Motivational**: Inspiring, empowering language

## Example Output

```
Title: The Benefits of Regular Exercise
Style: motivational

## Introduction

In today's world, the benefits of regular exercise has become increasingly 
essential. This article explores the key aspects that every fitness beginners 
should know. By the end, you'll have a comprehensive understanding of the subject.

## Key Concepts

When it comes to key concepts, there are several essential factors to consider...
```

## Customization

Modify `utils/writing_tools.py` to:
- Add new writing styles
- Change outline generation logic
- Customize content templates
- Adjust style transformations

Perfect for demonstrating complex multi-stage workflows!