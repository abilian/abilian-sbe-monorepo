# TODO

## P1

- [x] Fix and unskip tests in `tests/`
- [x] Make it work under Python 3.12 (for this, we need to upgrade Celery or get rid of it).
- [ ] Make a default app
- [ ] Make it work on Hop3 and Nua
- [ ] Migrate Flask-Tailwind to Flask-Vite


## P2

- [x] Remove Celery -> Dramatiq
- [ ] Replace "get_service" (and the service framework) with svcs
- [ ] Tailwind design
- [ ] Upgrade to SQLAlchemy 2
- [ ] Use SQLA 2 API

## P3

- [ ] Simplify design: 1 group <-> 1 community (?)
- [ ] Simplify permission system (use OSO or similar)
- [ ] Replace Flask (?)


## Fixes

### Typing issues

mypy: Found 443 errors in 122 files (checked 335 source files)
pyright: 1073 errors, 1 warning, 0 informations
