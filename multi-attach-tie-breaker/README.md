# Kubernetes PVC Multiattach Error Resolver Service

## Introduction

This service is designed to address the common problem in Kubernetes (k8s) where pods with PersistentVolumeClaims (PVCs) encounter a multiattach error upon being moved to another node. The multiattach error can cause delays in resolving pod scheduling and can impact application availability.

The purpose of this service is to provide a dedicated solution for quickly resolving the multiattach error and ensuring smooth operation of applications utilizing PVCs in a Kubernetes cluster.

## How It Works

The PVC Multiattach Error Resolver Service monitors the Kubernetes cluster for pods encountering multiattach errors due to PVCs. When such an error is detected, the service intervenes by performing the necessary actions to resolve the error and ensure that the affected pod can be scheduled and run successfully on the desired node.

## Installation

To install the PVC Multiattach Error Resolver Service in your Kubernetes cluster, follow these steps:

1. Clone the repository:
2. Feel free to build the image and push to your directory (check makefile for that)
3. Install the app using the provided helm charts ... apart form the pod we also need the related rbac to be able to perform ops against the entire cluster ... 
