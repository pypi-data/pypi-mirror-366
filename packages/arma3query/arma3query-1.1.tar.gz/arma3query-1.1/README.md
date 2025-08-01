# arma3query

Small Python module to decode the Arma 3 rules binary response.

## Requirements

Python >= 3.10, [python-a2s](https://github.com/Yepoleb/python-a2s)

## Install

`pip3 install arma3query`

## API

### Functions

* `arma3query.arma3rules(address, timeout=DEFAULT_TIMEOUT, encoding=DEFAULT_ENCODING)`
* `async arma3query.arma3rules_async(address, timeout=DEFAULT_TIMEOUT, encoding=DEFAULT_ENCODING)`
* `arma3query._parse_rules_data(rules_resp, encoding=DEFAULT_ENCODING)`

`_parse_rules_data` decodes a `a2s.rules(encoding=None)` response, the other functions work just like their a2s counterpart.

### Return Values

All functions return an ArmaRules instance. Some documentation is included in the source file.

## Authors

Built by [@jishnukarri](https://github.com/jishnukarri)  
Worked on with [@Benkol003](https://github.com/Benkol003)

## License

MIT
