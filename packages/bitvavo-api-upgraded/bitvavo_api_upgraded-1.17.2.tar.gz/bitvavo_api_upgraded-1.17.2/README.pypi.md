# Bitvavo API (upgraded)

Hi, this is *not* the official API, but this one has:

- build-in documentation
- typing for *all* functions and classes
- unit tests (I already found ~~three~~ ~~four~~ ~~five~~ six bugs that I fixed,
  because the original code wasn't tested, at all)
- a changelog, so you can track the changes that I make
- compatible with Python 3.9 and newer
- a working version of `getRemainingLimit()`
- will actually wait until the ban has been lifted (in case you get banned)
  (2024-11-24: this has now has been fixed - Bitvavo broke it in 2022, as they
  changed their website's API; can't blame them for not taking this non-standard
  SDK into account though. No hate)
- more stable api-calls, due to calculating lag between client and server
- fancy logging via `structlog`, including external loggers like from the
  urllib3 and websocket libs!
- a working `ACCESSWINDOW` variable that actually times the api calls out -
  makes failing Bitvavo API calls fail faster!

Version `1.*` is guaranteed compatible\* with the original API.

\*: Except for `Bitvavo.candles`. I had to renamed the `symbol` argument to
`market`, because the `candles` call actually excpects a `market`. So that's
more of a bugfix.

\*\*: Same goes for `Bitvavo.book`; it had the same problem as `candles`.

\*\*\*: And I removed the `rateLimitThread` class, but that should've been used
internally only anyway

## Customizable settings

Through the magic of the python-decouple lib, when you use this lib, you can
create a `settings.ini` (Windows
[example](https://pypi.org/project/python-decouple/#ini-file)) or a `.env`
(Linux [example](https://pypi.org/project/python-decouple/#env-file)) and add
some handy settings there.

Here is an example list of the settings for this lib:

```ini
# needed for the private part of the API
BITVAVO_APIKEY=
BITVAVO_APISECRET=

BITVAVO_API_UPGRADED_LOG_LEVEL=INFO  # Set the lib's log level
BITVAVO_API_UPGRADED_LOG_EXTERNAL_LEVEL=WARNING  # Set the libs that are used by *this* lib's log level
BITVAVO_API_UPGRADED_LAG=50  # the time difference between the server and your local time (you'll have to calculate this yourself - tip: use the bitvavo.time() functionality in a separate script)
BITVAVO_API_UPGRADED_RATE_LIMITING_BUFFER=25  # default 25, set to 50 if you get "you have been banned" messages (or even higher, if needed)
```

## Links

- [Official API Documentation](https://docs.bitvavo.com/)
- [Official Trading Rules](https://bitvavo.com/en/trading-rules) (recommended
  read, as it explains a lot of jargon; It's OK to not understand this document
  if you're just starting out - I don't fully understand the document either)
- [Github for this lib](https://github.com/Thaumatorium/bitvavo-api-upgraded)
