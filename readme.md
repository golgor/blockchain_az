This repository is the resulting code from following the course Blockchain A-Z.

Steps:
1. Clone repository
2. Make sure you have all dependencies installed, otherwise use pip to install
3. Run script
4. Server is running. Postman or web browser can be used to interact, use http://127.0.0.1:5000/<method>

Methods:
getChain - Print out the full chain as a JSON object.
mineBlock - Mine a new block.
checkValidity - Check to make sure the chain is consistens and that the hashes is correct.

Example:
Go to the following address using your browser:
    http://127.0.0.1:5000/getChain

Print out in the browser should be a JSON object. If this is the first method you are using the result should be:
{
  "chain": [
    {
      "index": 1,
      "previousHash": "0",
      "proof": 1,
      "timestamp": "Sun, 01 Jul 2018 14:24:09 GMT"
    }
  ],
  "length": 1
}
