// Set your desired cutoff frequency and sampling rate
const float cutoffFrequency = 70; // Cutoff frequency in Hz
const float samplingFrequency = 2048; // Sampling frequency in Hz

// Calculated constants
float alpha;
float previousOutput1 = 0.0, previousOutput2 = 0.0, previousOutput3 = 0.0; // For three stages

// variables
float input;
float output1, output2, output3; // Outputs of each filter stage

void setup() {
  Serial.begin(115200);
  
  // Calculate alpha based on the cutoff frequency and sampling frequency
  float dt = 1.0 / samplingFrequency;
  float RC = 1.0 / (2.0 * PI * cutoffFrequency);
  alpha = dt / (RC + dt);
}

void loop() {
  if (Serial.available()) {
    input = Serial.parseFloat();
    Serial.read(); // Clear '\n' from input buffer

    // Apply the first stage of the IIR filter
    output1 = alpha * input + (1 - alpha) * previousOutput1;

    // Apply the second stage of the IIR filter
    output2 = alpha * output1 + (1 - alpha) * previousOutput2;

    // Apply the third stage of the IIR filter
    output3 = alpha * output2 + (1 - alpha) * previousOutput3;

    // Print the filtered output from the third stage
    Serial.println(output3, 6);

    // Save the current outputs for the next iteration
    previousOutput1 = output1;
    previousOutput2 = output2;
    previousOutput3 = output3;
  }
}
