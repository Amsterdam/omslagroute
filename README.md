# Omslagroute

# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)

# Local Development

Start the dev server for local development:
```bash
docker-compose -f docker-compose.local.yml up
```

Create superuser:
```bash
python manage.py initadmin --settings settings.settings --username <EMAIL> --password <PASSWORD>
```

Go to http://localhost:8088/

For the admin interface:
http://localhost:8088/admin/

## Importing fixtures dump
The Django project needs some configuration in order to run locally. It's possible to add these manually, but the quickest way is importing using fixtures from the acceptance environment. You can download these automatically at:https://acc.omslagroute.amsterdam.nl/admin/dumpdata. You'll need to be logged in using an admin account first to access this url.

Move the json into the `app` directory on the root of your project, and run the following command

```bash
docker-compose -f docker-compose.local.yml run --rm omslagroute python manage.py loaddata <name of fixture>
```
Remove the json fixture after installing it.

## Build

To rebuild (for example, when dependencies are added requirements.txt):
```bash
docker-compose -f docker-compose.local.yml build
```

Start watching static files changes scss:

```bash
docker-compose -f docker-compose.local.yml exec omslagroute ./node_modules/.bin/node-sass -o ./assets/bundles/ static_src/sass --watch
```

Start watching static files changes js, vue:

```bash
docker-compose -f docker-compose.local.yml exec omslagroute ./node_modules/.bin/webpack --config webpack.config.js --watch
```

Migrate database without restarting containers:

```bash
docker-compose -f docker-compose.local.yml exec omslagroute python manage.py migrate
```

# Styling resources

The city of Amsterdam has developed a [design system](https://designsystem.amsterdam.nl/7awj1hc9f/p/39359e-design-system). Not all patterns have been built, they are built as soon as they become applicable. Ask colleagues through the OIS Slack #frontend channel.

The documentation for (React) components based on elements from the design system can be found in the [storybook](https://amsterdam.github.io/amsterdam-styled-components/?path=/story/experimental-atoms-accordion--single-accordion-with-paragraph) pages of the [Amsterdam Styled Components repository](https://github.com/Amsterdam/amsterdam-styled-components/tree/master/.storybook).
