"""Contract aggregation and deduplication logic."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models.contract import Contract
from src.models.source import DataSource, SourceStatus
from src.utils.logger import get_logger

logger = get_logger("aggregator")


class ContractAggregator:
    """Aggregates and deduplicates contract data from multiple sources."""

    def __init__(self, db: Session):
        """Initialize the aggregator."""
        self.db = db

    def save_contracts(self, contracts: List[Contract], source: DataSource) -> dict:
        """Save contracts to database with deduplication.

        Returns statistics about the operation.
        """
        stats = {
            "new": 0,
            "updated": 0,
            "unchanged": 0,
            "errors": 0,
        }

        for contract in contracts:
            try:
                # Check if contract already exists
                existing = self.db.query(Contract).filter(
                    and_(
                        Contract.source_id == contract.source_id,
                        Contract.external_id == contract.external_id,
                    )
                ).first()

                if existing:
                    # Update existing contract
                    if self._has_changes(existing, contract):
                        self._update_contract(existing, contract)
                        stats["updated"] += 1
                        logger.debug(f"Updated contract: {contract.external_id}")
                    else:
                        stats["unchanged"] += 1
                else:
                    # Add new contract
                    self.db.add(contract)
                    stats["new"] += 1
                    logger.debug(f"Added new contract: {contract.external_id}")

            except Exception as e:
                logger.error(f"Error saving contract {contract.external_id}: {e}")
                stats["errors"] += 1
                continue

        # Commit changes
        try:
            self.db.commit()

            # Update source statistics
            source.total_contracts_found += stats["new"]
            source.last_success_at = datetime.utcnow()
            source.total_scrapes += 1
            self.db.commit()

            logger.info(
                f"Saved contracts for {source.name}: "
                f"{stats['new']} new, {stats['updated']} updated, "
                f"{stats['unchanged']} unchanged, {stats['errors']} errors"
            )

        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            self.db.rollback()
            raise

        return stats

    def _has_changes(self, existing: Contract, new: Contract) -> bool:
        """Check if contract data has changed."""
        fields_to_check = [
            "title",
            "description",
            "agency",
            "department",
            "budget_min",
            "budget_max",
            "estimated_value",
            "due_date",
            "close_date",
            "status",
            "category",
            "contact_name",
            "contact_email",
            "contact_phone",
        ]

        for field in fields_to_check:
            old_val = getattr(existing, field)
            new_val = getattr(new, field)

            if old_val != new_val:
                return True

        return False

    def _update_contract(self, existing: Contract, new: Contract):
        """Update existing contract with new data."""
        existing.title = new.title
        existing.description = new.description
        existing.agency = new.agency
        existing.department = new.department
        existing.budget_min = new.budget_min
        existing.budget_max = new.budget_max
        existing.estimated_value = new.estimated_value
        existing.posted_date = new.posted_date
        existing.due_date = new.due_date
        existing.close_date = new.close_date
        existing.status = new.status
        existing.category = new.category
        existing.naics_code = new.naics_code
        existing.set_aside = new.set_aside
        existing.contact_name = new.contact_name
        existing.contact_email = new.contact_email
        existing.contact_phone = new.contact_phone
        existing.raw_data = new.raw_data
        existing.last_scraped_at = datetime.utcnow()
        existing.updated_at = datetime.utcnow()

    def find_duplicates(self) -> List[tuple]:
        """Find potential duplicate contracts across different sources.

        Uses title similarity and other heuristics.
        """
        # This is a simplified version - in production, you'd use
        # more sophisticated text similarity algorithms
        duplicates = []

        contracts = self.db.query(Contract).all()

        for i, c1 in enumerate(contracts):
            for c2 in contracts[i + 1:]:
                # Skip if same source
                if c1.source_id == c2.source_id:
                    continue

                # Check for similar titles
                if self._are_titles_similar(c1.title, c2.title):
                    # Additional checks
                    if (
                        c1.agency == c2.agency
                        or c1.due_date == c2.due_date
                        or (
                            c1.estimated_value
                            and c2.estimated_value
                            and abs(c1.estimated_value - c2.estimated_value) < 100
                        )
                    ):
                        duplicates.append((c1.id, c2.id))

        return duplicates

    def _are_titles_similar(self, title1: str, title2: str, threshold: float = 0.8) -> bool:
        """Check if two titles are similar using simple token overlap."""
        if not title1 or not title2:
            return False

        # Simple word overlap similarity
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())

        if not words1 or not words2:
            return False

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        similarity = intersection / union
        return similarity >= threshold

    def get_statistics(self) -> dict:
        """Get overall aggregation statistics."""
        from src.models.contract import ContractStatus

        total = self.db.query(Contract).count()
        open_contracts = (
            self.db.query(Contract)
            .filter(Contract.status == ContractStatus.OPEN)
            .count()
        )
        closed = (
            self.db.query(Contract)
            .filter(Contract.status == ContractStatus.CLOSED)
            .count()
        )

        # Group by state
        by_state = {}
        states = self.db.query(Contract.state).distinct().all()
        for (state,) in states:
            count = self.db.query(Contract).filter(Contract.state == state).count()
            by_state[state or "Unknown"] = count

        # Group by source
        by_source = {}
        sources = self.db.query(DataSource).all()
        for source in sources:
            count = (
                self.db.query(Contract)
                .filter(Contract.source_id == source.id)
                .count()
            )
            by_source[source.name] = count

        return {
            "total_contracts": total,
            "open_contracts": open_contracts,
            "closed_contracts": closed,
            "by_state": by_state,
            "by_source": by_source,
            "last_updated": datetime.utcnow().isoformat(),
        }
