// Sample JavaScript file with intentional issues for testing validators
// This file demonstrates various linting and formatting issues

// Issue: unused variable
const unusedVariable = "This variable is never used";

// Issue: inconsistent quotes
const message = "Hello World"
const name = 'John Doe'; // Mixed quotes

// Issue: missing semicolon
const age = 30

// Issue: long line that exceeds typical line length limits (usually 80-100 chars)
const veryLongString = "This is a very long string that exceeds the recommended maximum line length and should be wrapped or broken into multiple lines for better readability";

// Issue: console.log (often flagged in production code)
console.log("Debug message");

// Issue: inefficient code
function addNumbers(a, b) {
    if (a > 0) {
        if (b > 0) {
            return a + b;
        }
    }
    return 0;
}

// Issue: unused parameter
function greet(name, title) {
    return `Hello ${name}`;
}

// Issue: no error handling
function riskyOperation() {
    const data = JSON.parse('invalid json');
    return data;
}

// Issue: magic numbers
function calculatePrice(quantity) {
    return quantity * 9.99 + 5.50;
}

// Issue: inconsistent spacing
const numbers=[1,2,3,4,5];
const object={key:'value',another:  'value'};

// Issue: var instead of const/let
var oldStyleVariable = "Should use const or let";

// Good code for comparison
const SHIPPING_COST = 5.50;
const ITEM_PRICE = 9.99;

function calculateTotalPrice(quantity) {
    if (typeof quantity !== 'number' || quantity < 0) {
        throw new Error('Invalid quantity');
    }
    return quantity * ITEM_PRICE + SHIPPING_COST;
}

module.exports = {
    addNumbers,
    greet,
    calculateTotalPrice
};