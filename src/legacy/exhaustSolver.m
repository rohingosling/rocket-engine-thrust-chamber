%-----------------------------------------------------------------------------
% Project: Filleted Rocket Engine Thrust Chamber Contour Model
% Version: 1.0
% Date:    2017
# Author:  Rohin Gosling
%
% Function Description:
%
%   Solve for the coefficients of the contour model functions.
% 
%-----------------------------------------------------------------------------

function [ a0, b0, c0, a1, b1, y1 ] = exhaustSolver

    % Clear workspace and command window.

    clear;
    clc;

    % Define symbolic variables.

    syms x0 y0;     % p0
    syms x1 y1;     % p1
    syms x2 y2;     % p2
    syms a0 b0 c0;  % Coeficients of f(x)
    syms a1 b1;     % Coeficients of g(x)

    % Solve for the coefficients of the contour model functions.    
        
    [ a0, b0, c0, a1, b1, y1 ] = solve      ...
    (                                       ...
        0  == 2*a0*x0    + b0,              ... % f'(x0)=0      ...p0 is a turning point.
        y0 ==   a0*x0.^2 + b0*x0 + c0,      ... %  f(x0)=y0     ...f(x) at p0.        
        y1 ==   a0*x1.^2 + b0*x1 + c0,      ... %  f(x1)=y1     ...f(x) at p1.            
        y1 ==   a1*x1    + b1,              ... %  g(x1)=y1     ...g(x) at p1.
        y2 ==   a1*x2    + b1,              ... %  g(x2)=y2     ...g(x) at p2.
        a1 == 2*a0*x1    + b0,              ... % g'(x1)=f'(x1) ...The gradient of f(x) and g(x), is equal at p1. 
        a0, b0, c0,                         ... % Coeficients of f(x).
        a1, b1,                             ... % Coeficients of g(x).
        y1                                  ... % Value of y1 at x1.
    );
        
end


