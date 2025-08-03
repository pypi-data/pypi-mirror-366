# share-links

Small fast django website that allows you to share links (kinda like shaarli but using Django).

> Version 1.0.2 | [Main website](https://share-links.l3m.in) | [Documentation](https://doc.share-links.l3m.in/) | ![PyPI - Downloads](https://img.shields.io/pypi/dm/share-link?style=flat-square&label=install)

## Screenshots

| ![website screenshot](https://gitlab.com/sodimel/share-links/uploads/9881b550aa2671804aaf92d2493d5901/image.png) | ![mobile screenshot](https://gitlab.com/sodimel/share-links/uploads/ede7cf7f5600f12b95401d1a72fe426b/image.png) | ![admin interface with filters & custom columns](https://gitlab.com/sodimel/share-links/uploads/fc96983d9f920a1aa1bf882a63e33c85/image.png) |
| ---      | ---      | ---- |
| view on computer | view on smartphone | admin interface with filters & custom columns |

## Get started

- [Install the app on an existing project](docs/install/existing_project.md)
- [Install the app using the dedicated website](docs/install/dedicated_website.md)

> All content is also available in the [documentation](https://doc.share-links.l3m.in/).
> ##### Want a django website with this app already installed? Then check out [share-links-website](https://gitlab.com/sodimel/share-links-website)!

## Features

*Non exhaustive list*

- **Pages**
  - List and detail pages of links and tags and categories and collections
  - About me and contact page
- **Various filters**
  - Recent/oldest/featured/recently updated/by site/highlighted
  - Powerful **search**
- Save **Links** (with a title, a description and a few other options)
    - Organize them using **Tags** or **Categories**
    - Group them in **Collections** (e.g., favorite artists)
    - Display **favicons** before links (can be disabled)
    - Visit a **random link**!!1!
    - **Add multiple tags** to multiple links ([more infos here](https://gitlab.com/sodimel/share-links/-/issues/24#note_1714123948))
- **Django**-related features
    - **Admin interface** (add/edit/remove links/tags/[...])
        - Automatically **fetches page title and meta description** when adding a link
        - And some **custom actions**!
    - **Multiple accounts**
    - **Translations**
    - **Dead link check & web archive replacement** using some management commands
    - **Comment system** (with comment moderation)
    - **Export** content (json using `dumpdata`)
- **Fixtures** (provide a default list of categories and tags, translated in fr & en)
- **RSS feed**
- **Fetch website content** (in pdf, using weasyprint)
- **Web archive link display**
- **Statistics**
- A **webring** of different instances!!1!
- **Lots of config options**
- **It's f a s t** (i haven't tested it with more than ~3k links but it runs fine using sqlite as a db on an old dell optiplex fx160 with 3 gb of ram & an old intel atom 230)
- **Tests**
- **Extensive documentation**
