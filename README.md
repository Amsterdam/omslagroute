# fixxx-omslagroute

# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)

# Local Development

Start the dev server for local development:
```bash
docker-compose up
```

Go to http://localhost:8088/

Initial user and password in docker-compose.

For the admin interface:
http://localhost:8088/admin/


## Build

To rebuild (for example, when dependencies are added requirements.txt):
```bash
docker-compose build
```

Start watching static files changes scss:

```bash
docker-compose exec web ./node_modules/.bin/node-sass -o ./assets/bundles/ static_src/sass --watch
```

Start watching static files changes js, vue:

```bash
docker-compose exec web ./node_modules/.bin/webpack --config webpack.config.js --watch
```

Migrate database without restarting containers:

```bash
docker-compose exec web python manage.py migrate
```

# Styling resources

The city of Amsterdam has developed a [design system](https://designsystem.amsterdam.nl/7awj1hc9f/p/39359e-design-system). Not all patterns have been built, they are built as soon as they become applicable. Ask colleagues through the OIS Slack #frontend channel.

The documentation for (React) components based on elements from the design system can be found in the [storybook](https://amsterdam.github.io/amsterdam-styled-components/?path=/story/experimental-atoms-accordion--single-accordion-with-paragraph) pages of the [Amsterdam Styled Components repository](https://github.com/Amsterdam/amsterdam-styled-components/tree/master/.storybook).


# UX designs

[Figma](https://www.figma.com/file/CYyugtNLULjfyubpkXySlz/Brainstorm-omslagroute)

[Sketch Cloud](https://sketch.cloud/s/o5W1Q)