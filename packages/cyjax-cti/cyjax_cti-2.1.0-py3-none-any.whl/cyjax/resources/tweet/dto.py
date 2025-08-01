from cyjax.resources.model_dto import ModelDto


class TweetDto(ModelDto):

    @property
    def id(self) -> str:
        """
        The model identifier.
        :rtype str:
        """
        return self.get('id')

    @property
    def tweet_id(self) -> str:
        """
        The tweet ID.
        :rtype str:
        """
        return self.get('tweet_id')

    @property
    def tweet(self) -> str:
        """
        The tweet message.
        :rtype str:
        """
        return self.get('tweet')

    @property
    def author(self) -> str:
        """
        The tweet author.
        :rtype str:
        """
        return self.get('author')

    @property
    def link(self) -> str:
        """
        The link to the tweet.
        :rtype str:
        """
        return self.get('link')

    @property
    def timestamp(self) -> str:
        """
        The timestamp in ISO8601 format.
        :rtype str:
        """
        return self.get('timestamp')

    def __repr__(self):
        return '<TweetDto id={}>'.format(self.id)
