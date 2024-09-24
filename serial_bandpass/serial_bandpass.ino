// Set your desired cutoff frequencies and sampling rate
const float lowCutoffFrequency = 10; // Low cutoff frequency in Hz
const float highCutoffFrequency = 100; // High cutoff frequency in Hz
const float samplingFrequency = 2048; // Sampling frequency in Hz

// Calculated constants
float alphaHigh, alphaLow;
float previousInputHigh = 0.0;
float previousOutputHigh = 0.0;
float previousOutputLow = 0.0;

// Variables for input and output
float input;
float output;

void setup() {
  Serial.begin(115200);
  
  // Calculate alpha values for both high-pass and low-pass filters
  float dt = 1.0 / samplingFrequency;

  // High-pass filter constants
  float RCHigh = 1.0 / (2.0 * PI * lowCutoffFrequency);
  alphaHigh = RCHigh / (RCHigh + dt);

  // Low-pass filter constants
  float RCLow = 1.0 / (2.0 * PI * highCutoffFrequency);
  alphaLow = dt / (RCLow + dt);
}

void loop() {
  if (Serial.available()) {
    input = Serial.parseFloat();
    Serial.read(); // Clear the newline character

    // Apply the high-pass filter (removes frequencies below lowCutoffFrequency)
    float highPassOutput = alphaHigh * (previousOutputHigh + input - previousInputHigh);

    // Apply the low-pass filter (removes frequencies above highCutoffFrequency)
    output = alphaLow * highPassOutput + (1 - alphaLow) * previousOutputLow;

    // Print the filtered output
    Serial.println(output, 7);

    // Save the current input/output for the next iteration (for both filters)
    previousInputHigh = input;
    previousOutputHigh = highPassOutput;
    previousOutputLow = output;
  }
}
