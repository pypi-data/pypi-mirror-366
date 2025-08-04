#!/usr/bin/env python3
"""
Demonstration of the multivariate derivatives functionality in pydelt.

This script shows how to use the MultivariateDerivatives class to compute
gradients, Jacobians, Hessians, and Laplacians for multivariate functions.
"""

import numpy as np
import matplotlib.pyplot as plt
from src.pydelt.multivariate import MultivariateDerivatives
from src.pydelt.interpolation import SplineInterpolator, LlaInterpolator

def main():
    print("🚀 Multivariate Derivatives Demonstration")
    print("=" * 50)
    
    # Create test data for a 2D scalar function: f(x,y) = x^2 + y^2
    print("\n1. Setting up test data...")
    x = np.linspace(-2, 2, 20)
    y = np.linspace(-2, 2, 20)
    X, Y = np.meshgrid(x, y)
    
    # Input data: (x, y) coordinates
    input_data = np.column_stack([X.flatten(), Y.flatten()])
    
    # Scalar function: f(x,y) = x^2 + y^2
    scalar_output = (X**2 + Y**2).flatten()
    
    # Vector function: [x^2 + y^2, x + y]
    vector_output = np.column_stack([
        (X**2 + Y**2).flatten(),
        (X + Y).flatten()
    ])
    
    print(f"Input shape: {input_data.shape}")
    print(f"Scalar output shape: {scalar_output.shape}")
    print(f"Vector output shape: {vector_output.shape}")
    
    # Test with different interpolators
    interpolators = [
        ("Spline", SplineInterpolator, {"smoothing": 0.1}),
        ("LLA", LlaInterpolator, {"window_size": 5})
    ]
    
    for name, interp_class, kwargs in interpolators:
        print(f"\n2. Testing with {name} Interpolator")
        print("-" * 30)
        
        # Initialize multivariate derivatives
        mv = MultivariateDerivatives(interp_class, **kwargs)
        mv.fit(input_data, scalar_output)
        
        # Test point
        test_point = np.array([[1.0, 1.0]])
        print(f"Test point: {test_point[0]}")
        
        # Compute gradient
        gradient_func = mv.gradient()
        grad = gradient_func(test_point)
        print(f"Gradient: {grad.flatten()}")
        print(f"Expected: [2.0, 2.0] (analytical: [2x, 2y])")
        
        # Compute Hessian
        hessian_func = mv.hessian()
        hess = hessian_func(test_point)
        print(f"Hessian diagonal: {np.diag(hess)}")
        print(f"Expected: [2.0, 2.0] (analytical: [2, 2])")
        
        # Compute Laplacian
        laplacian_func = mv.laplacian()
        lap = laplacian_func(test_point)
        print(f"Laplacian: {lap[0]}")
        print(f"Expected: 4.0 (analytical: 2 + 2)")
        
        # Test with vector function
        print(f"\n3. Vector Function Test with {name}")
        mv_vector = MultivariateDerivatives(interp_class, **kwargs)
        mv_vector.fit(input_data, vector_output)
        
        jacobian_func = mv_vector.jacobian()
        jac = jacobian_func(test_point)
        print(f"Jacobian shape: {jac.shape}")
        print(f"Jacobian:\n{jac}")
        print("Expected for [x^2+y^2, x+y]: [[2x, 2y], [1, 1]] = [[2, 2], [1, 1]]")
        print("Note: Traditional interpolation approximates cross-terms as zero")
    
    print(f"\n4. Multiple Point Evaluation")
    print("-" * 30)
    
    # Test with multiple points
    test_points = np.array([[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]])
    mv = MultivariateDerivatives(SplineInterpolator, smoothing=0.1)
    mv.fit(input_data, scalar_output)
    
    gradient_func = mv.gradient()
    gradients = gradient_func(test_points)
    
    print(f"Test points shape: {test_points.shape}")
    print(f"Gradients shape: {gradients.shape}")
    print("Gradients at multiple points:")
    for i, (point, grad) in enumerate(zip(test_points, gradients)):
        print(f"  Point {point}: Gradient {grad}")
    
    print(f"\n✅ Multivariate derivatives demonstration complete!")
    print("The module successfully computes gradients, Jacobians, Hessians, and Laplacians")
    print("for both scalar and vector-valued multivariate functions.")

if __name__ == "__main__":
    main()
