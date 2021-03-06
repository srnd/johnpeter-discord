from database.rounds import Round


class Tournament(object):
    def __init__(self, game_name, tc_id, join_message_id, players_per_game=4, gamers=None, rounds=None):
        """
        :param game_name: The game name
        :param tc_id: The ID of the text channel the tournament was created in
        :param join_message_id: The ID of the message that users react to to participate in the tournament
        :param players_per_game: the maximum amount of players for each matchup
        :param gamers: A list of participants by member ID
        :param rounds: A list of Round objects
        """
        self.game_name = game_name
        self.tc_id = tc_id
        self.join_message_id = join_message_id
        self.players_per_game = players_per_game
        if gamers is None:
            gamers = []
        self.gamers = gamers
        if rounds is None:
            rounds = []
        self.rounds = rounds

    @staticmethod
    def from_dict(source):
        tournament = Tournament(game_name=source['game_name'], tc_id=source['tc_id'],
                                join_message_id=source['join_message_id'], players_per_game=source['players_per_game'],
                                gamers=source['gamers'], rounds=[Round.from_dict(round) for round in source['rounds']])
        return tournament

    def to_dict(self):
        dest = {
            'game_name': self.game_name,
            'tc_id': self.tc_id,
            'join_message_id': self.join_message_id,
            'players_per_game': self.players_per_game,
            'gamers': self.gamers,
            'rounds': [round.to_dict() for round in self.rounds]
        }

        return dest

    async def next_round(self, bot=None):
        if not self.rounds:  # If no round already exists create one
            self.rounds = [Round(0,self.gamers, group_size=self.players_per_game)]
            if bot:
                await (await bot.get_channel(self.tc_id).fetch_message(self.join_message_id)).edit(
                    content=self.update_join_message(complete=True))
                self.join_message_id = (await bot.get_channel(self.tc_id).send(self.rounds[-1].generate_status_message())).id
            return True
        elif bot:
            for game in self.rounds[-1].games:
                await game.delete_channel(bot)
        r = self.rounds[-1]
        # Get latest round
        if r.round_complete():
            self.rounds.append(Round(len(self.rounds), r.winners(), group_size=self.players_per_game))
            if bot:
                self.join_message_id = (await bot.get_channel(self.tc_id).send(self.rounds[-1].generate_status_message())).id
            return True
        else:
            return False

    @staticmethod
    def make_join_message(game_name):
        return f'Please react to this message with :trophy: to join the {game_name} Tournament!'

    def update_join_message(self, complete=False):
        if complete:
            out = f'The {self.game_name} Tournament has started!'
        else:
            out = self.make_join_message(self.game_name)
        out += f'\n{len(self.gamers)} gamers currently registered'
        if len(self.gamers) < 50:
            out += ':'
            for gamer in self.gamers:
                out += f'\n <@{gamer}>'
        return out

    def add_gamer(self,gamer):
        if not self.rounds:  # don't add someone if tourney already started
            self.gamers.append(gamer)
            return True
        else:
            return False

    def remove_gamer(self,gamer):
        if not self.rounds:  # don't remove someone if tourney already started
            if gamer in self.gamers:
                self.gamers.remove(gamer)
            return True
        else:
            return False

    async def join_message(self, bot):
        return await bot.get_channel(self.tc_id).fetch_message(self.join_message_id)

    async def delete(self, bot):
        if self.rounds:
            for game in self.rounds[-1].games:
                await game.delete_channel(bot)
        else:
            m = await self.join_message(bot)
            await m.delete()

    async def broadcast(self, message, bot):
        for game in self.rounds[-1].games:
            await bot.get_channel(game.tc_id).send(message + ' ' + ''.join([f'<@{gamer}> ' for gamer in self.gamers]))
